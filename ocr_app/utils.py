import os
import io
from google.cloud import vision

# Setup Kunci API Google
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_KEY_PATH', 'google_key.json')

def extract_text_from_image(image_bytes):
    """
    Ekstraksi teks menggunakan Google Cloud Vision API dengan penanganan error yang benar.
    """
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    
    # Gunakan DOCUMENT_TEXT_DETECTION untuk hasil terbaik pada tulisan tangan
    response = client.document_text_detection(image=image)
    
    if response.error.message:
        # Lempar exception agar bisa ditangkap oleh views.py
        raise Exception(f"Google Vision API Error: {response.error.message}")

    if not response.text_annotations:
        return ""

    return format_vision_to_table(response)

def format_vision_to_table(response):
    """
    Algoritma Column Bucketing: Mencegah kolom bergeser (Shifting) 
    akibat adanya sel tabel yang kosong.
    """
    words = []
    for annotation in response.text_annotations[1:]:
        text = annotation.description.strip()
        if not text: continue
        
        v = annotation.bounding_poly.vertices
        y_min = min(v[0].y, v[2].y)
        y_max = max(v[0].y, v[2].y)
        x_min = min(v[0].x, v[1].x)
        x_max = max(v[0].x, v[1].x)
        
        words.append({
            'text': text, 
            'y_min': y_min, 
            'y_max': y_max, 
            'x_min': x_min,
            'x_max': x_max,
            'x_center': (x_min + x_max) / 2,
            'y_center': (y_min + y_max) / 2
        })

    if not words: return ""

    # --- TAHAP 1: Kelompokkan menjadi Baris (Row Grouping) ---
    words.sort(key=lambda x: x['y_center'])
    rows = []
    while words:
        current_word = words.pop(0)
        current_row = [current_word]
        l_y_min, l_y_max = current_word['y_min'], current_word['y_max']
        
        remaining = []
        for w in words:
            overlap = max(0, min(l_y_max, w['y_max']) - max(l_y_min, w['y_min']))
            if overlap > ((w['y_max'] - w['y_min']) * 0.4):
                current_row.append(w)
                l_y_min, l_y_max = (l_y_min + w['y_min'])/2, (l_y_max + w['y_max'])/2
            else:
                remaining.append(w)
        
        current_row.sort(key=lambda x: x['x_min'])
        rows.append(current_row)
        words = remaining

    # --- TAHAP 2: Cari Posisi Kolom Global (Column Bucketing) ---
    # Kita asumsikan baris pertama (header) memiliki posisi kolom yang benar
    if not rows: return ""
    header_row = rows[0]
    column_markers = [w['x_center'] for w in header_row]
    column_markers.sort()

    # --- TAHAP 3: Susun Ulang Kata ke dalam Bucket Kolom ---
    formatted_lines = []
    for row in rows:
        # Siapkan bucket kosong sebanyak jumlah kolom di header
        buckets = [""] * len(column_markers)
        
        for w in row:
            # Cari marker kolom terdekat untuk kata ini
            distances = [abs(w['x_center'] - marker) for marker in column_markers]
            best_column_idx = distances.index(min(distances))
            
            # Gabungkan jika ada lebih dari satu kata dalam satu sel
            if buckets[best_column_idx]:
                buckets[best_column_idx] += " " + w['text']
            else:
                buckets[best_column_idx] = w['text']
        
        formatted_lines.append(" | ".join(buckets))

    return "\n".join(formatted_lines)
