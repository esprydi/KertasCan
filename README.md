# 📄 KertasCan - OCR to Spreadsheet

**KertasCan** adalah aplikasi web berbasis Django yang dirancang untuk memindai dokumen (gambar) dan mengonversinya menjadi format spreadsheet (Excel) secara otomatis. Aplikasi ini menggabungkan kekuatan **Google Cloud Vision API** untuk deteksi teks (termasuk tulisan tangan) dan antarmuka **Jspreadsheet** untuk pengeditan data secara interaktif selayaknya menggunakan Microsoft Excel di browser.

---

## ✨ Fitur Utama

- **High-Accuracy OCR**: Menggunakan Google Cloud Vision (DOCUMENT_TEXT_DETECTION) yang sangat andal dalam membaca tabel, teks cetak, maupun tulisan tangan.
- **Interactive Spreadsheet Editor**: Edit hasil scan langsung di browser dengan fitur klik-dan-ketik, tambah/hapus baris/kolom, dan navigasi keyboard.
- **Excel Formula Support**: Mendukung penggunaan rumus Excel dasar seperti `=SUM()`, perkalian, pembagian, dll., langsung di dalam editor.
- **Export to Excel (.xlsx)**: Unduh hasil scan dan editan Anda ke dalam file Excel asli. Setiap dokumen yang di-scan akan menjadi *Sheet* terpisah di dalam satu file.
- **Stateless & Secure**: Data disimpan secara sementara di dalam *session* pengguna, memastikan privasi dan kecepatan tanpa memerlukan database yang berat.

---

## 🚀 Teknologi yang Digunakan

- **Backend**: Django 4.x (Python 3.x)
- **Frontend**: 
    - Bootstrap 5 (Styling)
    - Jspreadsheet CE v4 (Interactive Spreadsheet)
    - FontAwesome 6 (Icons)
- **Analisis Data**: 
    - Pandas (Data processing)
    - Openpyxl (Excel engine)
- **API**: Google Cloud Vision API

---

## 🛠️ Persiapan & Instalasi

### 1. Prasyarat
Pastikan Anda sudah menginstal Python 3.x di sistem Anda.

### 2. Kunci API Google Cloud
Aplikasi ini memerlukan kunci API Google Cloud Vision.
1. Buat proyek di [Google Cloud Console](https://console.cloud.google.com/).
2. Aktifkan **Cloud Vision API**.
3. Buat **Service Account** dan unduh kunci dalam format JSON.
4. Simpan file tersebut di direktori utama proyek dengan nama `google_key.json`.

### 3. Instalasi Dependensi
Jalankan perintah berikut untuk menginstal pustaka yang diperlukan:
```bash
pip install django google-cloud-vision pandas openpyxl
```

---

## 🏃 Cara Menjalankan

1. Pastikan file `google_key.json` sudah ada di folder utama.
2. Jalankan server pengembangan Django:
   ```bash
   python manage.py runserver
   ```
   *Atau gunakan file `run.bat` yang sudah disediakan (khusus Windows).*

3. Buka browser dan akses ke: `http://127.0.0.1:8000`

---

## 📂 Struktur Proyek Singkat

```text
kertascan/
├── core/                # Konfigurasi utama Django
├── ocr_app/             # Logika aplikasi (Views, Utils, Templates)
│   ├── utils.py         # Algoritma bucketing kolom OCR
│   ├── views.py         # Logika pengolahan data & Excel export
│   └── templates/       # Antarmuka pengguna (HTML)
├── google_key.json      # Kunci API Google (Jangan di-upload ke Git)
├── manage.py
└── README.md
```

---

## 📝 Lisensi
Proyek ini dibuat untuk tujuan portofolio dan pengembangan alat produktivitas mandiri.

---
**KertasCan** - *Ubah kertas menjadi data dalam sekejap.* 🚀
