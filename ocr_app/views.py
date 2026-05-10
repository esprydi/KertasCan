from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .utils import extract_text_from_image
import pandas as pd
import io
import os
import json

def home(request):
    """
    Halaman Utama untuk Upload Dokumen.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        image_bytes = image_file.read()
        
        try:
            extracted_text = extract_text_from_image(image_bytes)
            
            if not extracted_text.strip():
                messages.warning(request, "Teks tidak terdeteksi pada gambar tersebut.")
                return redirect('home')

            scanned_texts = request.session.get('scanned_texts', [])
            scanned_texts.append(extracted_text)
            request.session['scanned_texts'] = scanned_texts
            request.session.modified = True
            
            messages.success(request, "Dokumen berhasil di-scan!")
            return redirect('results')
            
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {str(e)}")
            return redirect('home')
    
    return render(request, 'ocr_app/upload.html')

def results(request):
    """
    Menampilkan daftar hasil scan.
    """
    scanned_texts = request.session.get('scanned_texts', [])
    return render(request, 'ocr_app/results.html', {'scanned_texts': scanned_texts})

def edit_result(request, index):
    """
    Mengedit hasil scan dengan antarmuka Excel (Spreadsheet).
    """
    scanned_texts = request.session.get('scanned_texts', [])
    if index >= len(scanned_texts):
        return redirect('results')
    
    if request.method == 'POST':
        # Ambil data dari Spreadsheet (JSON)
        excel_data_json = request.POST.get('excel_data')
        
        if excel_data_json:
            try:
                data_array = json.loads(excel_data_json)
                
                # Konversi Array of Arrays kembali ke format String '|'
                cleaned_rows = []
                for row in data_array:
                    if isinstance(row, list):
                        # Abaikan baris yang isinya kosong semua (efek dari minDimensions jspreadsheet)
                        if all(cell == "" or cell is None for cell in row):
                            continue
                        
                        # Hapus kolom kanan yang kosong agar data rapi
                        while len(row) > 0 and (row[-1] == "" or row[-1] is None):
                            row.pop()
                            
                        if not row:
                            continue
                            
                        # Gabungkan kolom, ganti None dengan string kosong
                        line = " | ".join([str(cell) if cell is not None else "" for cell in row])
                        cleaned_rows.append(line)
                
                new_text = "\n".join(cleaned_rows)
                
                if not new_text.strip():
                    messages.warning(request, "Data tabel kosong. Perubahan dibatalkan.")
                    return redirect('edit_result', index=index)
                    
                scanned_texts[index] = new_text
                request.session['scanned_texts'] = scanned_texts
                request.session.modified = True
                
                messages.success(request, "Perubahan berhasil disimpan ke database.")
                return redirect('results')
            except Exception as e:
                messages.error(request, f"Gagal memproses data tabel: {str(e)}")
        else:
            # Fallback jika spreadsheet gagal kirim data
            messages.warning(request, "Data tabel kosong atau tidak terkirim.")
            
        return redirect('results')
    
    # GET: Siapkan data JSON untuk Spreadsheet
    raw_text = scanned_texts[index]
    json_data = []
    for line in raw_text.split('\n'):
        if line.strip():
            cols = [c.strip() for c in line.split('|')]
            json_data.append(cols)
    
    # Berikan minimal 3 kolom jika kosong agar tidak error
    if not json_data:
        json_data = [["", "", ""]]

    return render(request, 'ocr_app/edit.html', {
        'json_data': json.dumps(json_data),
        'index': index
    })

def clear_session(request):
    """
    Menghapus semua data scan.
    """
    if 'scanned_texts' in request.session:
        del request.session['scanned_texts']
        request.session.modified = True
    messages.info(request, "Data berhasil dibersihkan.")
    return redirect('home')

def download_excel(request):
    """
    Membuat file Excel (.xlsx) dari data session. Setiap dokumen menjadi Sheet terpisah.
    """
    scanned_texts = request.session.get('scanned_texts', [])
    if not scanned_texts:
        return redirect('home')
        
    try:
        output = io.BytesIO()
        # Gunakan openpyxl untuk membuat file excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            has_valid_sheet = False
            for idx, doc_text in enumerate(scanned_texts):
                all_data_rows = []
                for line in doc_text.split('\n'):
                    if line.strip():
                        cols = [c.strip() for c in line.split('|')]
                        all_data_rows.append(cols)
                        
                if not all_data_rows:
                    continue

                # Pastikan panjang kolom sama di semua baris agar pandas tidak error
                max_cols = max(len(row) for row in all_data_rows)
                for row in all_data_rows:
                    while len(row) < max_cols:
                        row.append("")

                headers = all_data_rows[0]
                
                # Buat header unik
                unique_headers = []
                for i, h in enumerate(headers):
                    h_name = h if h else f"Kolom_{i+1}"
                    original_h_name = h_name
                    counter = 1
                    while h_name in unique_headers:
                        h_name = f"{original_h_name}_{counter}"
                        counter += 1
                    unique_headers.append(h_name)

                data_content = all_data_rows[1:]
                
                # Hindari baris duplikat dengan header (misal header terbawa di data)
                data_content = [row for row in data_content if row != headers]

                # Konversi data numerik & biarkan rumus tetap string
                final_data = []
                for row in data_content:
                    new_row = []
                    for cell in row:
                        val = str(cell).strip()
                        if val.startswith('='):
                            new_row.append(val)
                        else:
                            try:
                                if '.' in val: new_row.append(float(val))
                                else: new_row.append(int(val))
                            except ValueError:
                                new_row.append(val)
                    final_data.append(new_row)

                df = pd.DataFrame(final_data, columns=unique_headers)
                sheet_name = f'Dokumen {idx+1}'
                df.to_excel(writer, index=False, sheet_name=sheet_name)
                has_valid_sheet = True
                
        if not has_valid_sheet:
            messages.warning(request, "Tidak ada data valid untuk didownload.")
            return redirect('results')
            
        output.seek(0)
        
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=kertascan_results.xlsx'
        return response
    except Exception as e:
        messages.error(request, f"Gagal membuat file Excel: {str(e)}")
        return redirect('results')

