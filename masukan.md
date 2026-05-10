# Review dan Hasil Testing KertasCan OCR

Berdasarkan hasil analisis dan *testing* kode pada aplikasi KertasCan (terutama setelah adanya penambahan fitur antarmuka Jspreadsheet), ditemukan beberapa *bug* kritikal yang perlu segera diperbaiki agar aplikasi berjalan stabil dan sesuai dengan ekspektasi.

---

## 1. Bug Kritikal (Server Crash) pada Fitur Download Excel
**Lokasi**: `ocr_app/views.py` (Fungsi `download_excel`)

**Deskripsi Masalah**:
Saat ini, logika pengunduhan Excel menggabungkan **semua** hasil scan menjadi satu *Dataframe* (`all_data_rows`) menggunakan Pandas. 
Aplikasi akan mengalami *crash* (`ValueError: N columns passed, passed data had M columns`) jika terjadi kondisi berikut:
1. Pengguna memindai dua dokumen berbeda yang memiliki **jumlah kolom yang tidak sama** (misalnya Dokumen 1 memiliki 3 kolom, Dokumen 2 memiliki 4 kolom).
2. Pengguna mengedit salah satu dokumen di antarmuka Spreadsheet. Konfigurasi `minDimensions: [6, 12]` pada `edit.html` akan secara otomatis menambahkan kolom kosong hingga berjumlah 6 kolom. Saat digabungkan dengan dokumen lain yang belum diedit (misal masih 3 kolom), Pandas akan error karena panjang baris data menjadi tidak seragam.

**Solusi yang Disarankan**:
Ubah logika pada fungsi `download_excel` dengan salah satu cara berikut:
- **Opsi A (Paling Aman):** Buat *sheet* yang berbeda-beda untuk setiap dokumen (misal: "Dokumen 1", "Dokumen 2") di dalam satu file Excel, sehingga perbedaan kolom antar-dokumen tidak saling mengganggu.
- **Opsi B:** Berikan *padding* tambahan (mengisi dengan *string* kosong `""`) pada baris yang memiliki jumlah kolom lebih sedikit agar seragam dengan baris terpanjang sebelum dimasukkan ke dalam `pd.DataFrame`.

---

## 2. Fitur Rumus (Formula) Hilang Saat Disimpan
**Lokasi**: `ocr_app/templates/ocr_app/edit.html`

**Deskripsi Masalah**:
Di antarmuka Spreadsheet, Anda sudah mengaktifkan `parseFormulas: true` dan ada pengecekan untuk menampung rumus di `views.py`. NAMUN, di file `edit.html` baris ke-113, Anda menggunakan kode ini:
```javascript
const data = myTable.getData(true);
```
Parameter `true` pada fungsi `getData(true)` memaksa Jspreadsheet mengirimkan **data yang sudah dihitung (processed value)**, bukan teks aslinya. Akibatnya, jika pengguna mengetik rumus seperti `=A1+B1`, yang terkirim ke *backend* adalah hasilnya (misal `20`), sehingga rumusnya akan hilang permanen dan tidak tertulis sebagai rumus di Excel.

**Solusi yang Disarankan**:
Hapus parameter `true` saat mengambil data, ubah menjadi:
```javascript
const data = myTable.getData(); // Mengambil data mentah (termasuk rumus teks)
```

---

## 3. Data Kosong Jika Kolom/Baris Dihapus Semua
**Lokasi**: `ocr_app/views.py` (Fungsi `edit_result`)

**Deskripsi Masalah**:
Jika pengguna secara tidak sengaja menghapus semua isi tabel di editor lalu menekan "Simpan", sistem akan menyimpan string kosong (atau berisi *pipe* `|` kosong). Hal ini bisa menyebabkan index array di dalam `session` rusak atau dokumen menjadi tidak dapat dibaca sama sekali.

**Solusi yang Disarankan**:
Tambahkan validasi tambahan di dalam fungsi `edit_result` setelah pemrosesan JSON:
```python
if not new_text.strip().replace('|', ''):
    messages.warning(request, "Tabel tidak boleh kosong sepenuhnya.")
    return redirect('results')
```

---

## 4. Saran Non-Kode (Typo Perintah Terminal)
Dari log terminal, terlihat beberapa kali ada kesalahan ketik saat menjalankan server (seperti `pyton manege.py runserver`, `python manage.py run server`). Hal ini wajar, namun bisa memperlambat proses pengembangan.

**Solusi yang Disarankan**:
Buat file `run.bat` di dalam direktori `kertascan` yang isinya:
```bat
@echo off
python manage.py runserver
```
Sehingga ke depannya Anda cukup mengetikkan `./run.bat` di terminal.

---

## Kesimpulan
Aplikasi Anda sudah memiliki konsep integrasi OCR dan Spreadsheet yang sangat inovatif! Fokus perbaikan utama saat ini adalah memastikan **Dataframe Pandas tidak error saat ada perbedaan jumlah kolom** dan **mengamankan pengiriman teks rumus dari Jspreadsheet**. Silakan terapkan solusi di atas sebelum melanjutkan ke fase pengembangan fitur lainnya.
