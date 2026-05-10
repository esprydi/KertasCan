# Planning Project: KertasCan (OCR Dokumen ke Spreadsheet)

## 📌 Deskripsi Proyek
Proyek ini adalah aplikasi web berbasis **Django (Python)** yang memungkinkan pengguna untuk mengunggah gambar/foto dokumen fisik (kertas). Sistem akan membaca teks di dalam gambar menggunakan teknologi **OCR (Optical Character Recognition)**, mengekstrak datanya, menampilkannya ke pengguna, dan memungkinkan pengguna untuk mengunduh hasilnya dalam format **Spreadsheet (.xlsx / .csv)**.

---

## 🛠️ Teknologi yang Digunakan
- **Backend:** Python + Django
- **Frontend:** HTML, CSS (Bootstrap 5 agar simpel & responsif), Vanilla JavaScript (untuk interaksi dasar)
- **OCR Engine:** `easyocr` (Akurasi tinggi, sangat cocok untuk mendeteksi tulisan tangan) atau **Google Cloud Vision API**
- **Data Processing & Export:** `pandas` atau `openpyxl` (untuk membuat file Excel)
- **Database:** Tidak Ada (Stateless). Data disimpan sementara di dalam *Signed Cookie Session* browser agar sangat mudah di-deploy ke PaaS (Heroku, Vercel, Render) tanpa setup DB sama sekali.

---

## 🗺️ Alur Aplikasi (User Flow)
1. **Halaman Utama (Upload):** Pengguna melihat form untuk mengunggah gambar dokumen (JPG/PNG/PDF).
2. **Proses OCR:** Setelah gambar diunggah, server langsung memproses gambar menggunakan OCR untuk mengekstrak teks.
3. **Review Data:** Teks hasil ekstraksi ditampilkan di halaman web dalam bentuk tabel sederhana atau text area untuk dikoreksi manual jika ada salah deteksi.
4. **Iterasi (Upload Lagi):** Pengguna memiliki tombol "Upload Dokumen Lain" yang akan memproses gambar baru dan menambahkan hasilnya ke keranjang data (disimpan di Session atau Database).
5. **Download Spreadsheet:** Jika pengguna telah selesai mengumpulkan data, mereka dapat menekan tombol "Download Excel". Sistem akan mengubah seluruh tumpukan data tersebut menjadi file `.xlsx` dan mengirimkannya ke browser untuk diunduh secara online.

---

## 🚀 Langkah-Langkah Implementasi (Step-by-Step)

### Tahap 1: Persiapan Awal (Setup Project)
Tahap ini bertujuan untuk menyiapkan lingkungan kerja. Sangat mudah diikuti:

1. **Buat Virtual Environment:**
   ```bash
   python -m venv venv
   # Aktifkan di Windows:
   venv\Scripts\activate  
   ```
2. **Install Dependensi Utama:**
   ```bash
   pip install django easyocr Pillow pandas openpyxl
   ```
   *(Catatan: `easyocr` akan mengunduh model Deep Learning (PyTorch) dan model bahasanya secara otomatis saat pertama kali dijalankan. Proses ini butuh koneksi internet stabil).*
3. **Inisiasi Proyek Django:**
   ```bash
   django-admin startproject kertascan_project .
   python manage.py startapp ocr_app
   ```
4. Daftarkan `ocr_app` ke dalam `INSTALLED_APPS` di file `kertascan_project/settings.py`.

### Tahap 2: Konfigurasi Session (Stateless / Tanpa Database)
Karena Anda ingin langsung ke deployment tanpa repot mengurus database (Stateless), kita akan menyimpan teks OCR ke dalam *Cookie* di browser pengguna.

1. Buka `kertascan_project/settings.py`.
2. Tambahkan atau ubah pengaturan session menjadi berbasis Cookie:
   ```python
   SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
   ```
*(Dengan ini, kita tidak perlu membuat `models.py` dan tidak perlu menjalankan `migrate` database. Aplikasi tidak memerlukan koneksi DB).*

### Tahap 3: Pembuatan Fungsi OCR (Pemrosesan Inti)
Buat satu file khusus, misal `ocr_app/utils.py` untuk mengurus pemrosesan gambar ke teks agar rapi dan tidak bercampur dengan routing web.

1. Import `easyocr`.
2. Buat *reader instance* (`reader = easyocr.Reader(['id', 'en'])`) di luar fungsi utama agar model tidak diload berulang kali.
3. Buat fungsi `extract_text_from_image(image_bytes)` yang membaca file gambar langsung dari *memory* (tanpa di-save) lalu memanggil `reader.readtext(image_bytes, detail=0)`.
4. *(Tips: Hasil dari `readtext(detail=0)` adalah array/list of strings. Anda bisa langsung menggabungkannya dengan `\n` atau mengolahnya per baris).*

### Tahap 4: Pembuatan Views (Logika Utama Web)
Buka `ocr_app/views.py`. Kita hanya butuh 3 fungsi/halaman utama:

1. **`home` view (Untuk Upload):** 
   - Menampilkan form upload file.
   - Jika menerima request POST (gambar dikirim), baca file dari `request.FILES['image']`, dan langsung *passing* ke fungsi OCR di `utils.py` (gambar diproses langsung di RAM).
   - Simpan langsung *hasil teksnya* ke dalam array di **Django Session** (Contoh: `request.session['scanned_texts'] = ["teks hasil kertas 1", "teks hasil kertas 2"]`). Ini berfungsi seperti sistem "keranjang belanja".
   - Redirect pengguna ke halaman hasil (review).
2. **`results` view (Untuk Melihat Hasil):**
   - Mengambil array berisi daftar teks dari Session (`request.session.get('scanned_texts', [])`).
   - Mengirim array data teks tersebut ke template HTML agar bisa ditampilkan berupa list.
3. **`download_excel` view (Untuk Export Data):**
   - Mengambil data teks dari Session.
   - Menggunakan `pandas` untuk menyusun teks tersebut di dalam memori (`io.BytesIO`) menjadi kolom-kolom (DataFrame).
   - Mengubah file memori tersebut menjadi respons HTTP file bertipe Excel, sehingga otomatis terunduh saat diakses.
   - Bersihkan Session (`request.session.flush()`) setelah diunduh agar keranjang kosong lagi (opsional).

### Tahap 5: Pembuatan Templates (Tampilan / UI)
Buat folder `templates/` di dalam `ocr_app`. Gunakan framework **Bootstrap 5** (via link CDN) agar tidak pusing mengurus CSS secara manual dan langsung responsif (bisa dibuka di HP).

1. **`base.html`:** Layout induk yang memuat link Bootstrap, Navbar simpel ("KertasCan"), dan footer.
2. **`upload.html`:** Tampilan form sederhana dengan tombol besar. Berikan area putih di tengah untuk form input file.
3. **`results.html`:** 
   - Menampilkan *card* berisikan teks yang baru saja di-scan.
   - Sediakan tombol berukuran besar: 
     - **"➕ Tambah Dokumen Lain"** (link kembali ke form upload).
     - **"⬇️ Download Spreadsheet"** (link mengeksekusi view download_excel).

---

## 🔧 Panduan Modifikasi & Kustomisasi (Untuk Kedepannya)

Jika proyek versi *basic* di atas sudah jalan, Anda bisa memodifikasinya sesuai kebutuhan bisnis:

1. **Jika Server Terlalu Berat (Optimasi Deployment):**
   - Menggunakan `easyocr` memang **sangat akurat** untuk tulisan tangan, namun ia berbasis AI (PyTorch) sehingga memakan **RAM server yang cukup besar** (biasanya di atas 1 GB).
   - **Jika server gratisan Anda (PaaS) kehabisan RAM saat deploy:** Ganti `easyocr` dengan **Google Cloud Vision API**. Pemrosesan akan dilempar ke server Google sehingga server web Anda tetap sangat ringan. Google Vision juga gratis untuk 1000 gambar pertama setiap bulannya. Sisa kode (View, Session, UI) **TIDAK PERLU** diubah sama sekali.

2. **Parsing Data yang Rapi (Misal: Struk Belanja):**
   - Secara default OCR akan menghasilkan string panjang (teks mentah).
   - Jika Anda menscan KTP, Invoice, atau Form, buatlah fungsi *Regex (Regular Expression)* di Python sebelum data dimasukkan ke Excel.
   - Misal: Deteksi kata yang ada "Rp", lalu masukkan angka sebelahnya ke kolom "Harga".

3. **Merapikan UI / Tema:**
   - Anda dapat mencari template gratis Bootstrap, lalu tinggal memindahkan HTML-nya ke dalam file `templates/` proyek Anda. Tidak perlu mengedit kode backend sama sekali.

4. **Penyimpanan / Database Lanjutan (Opsional Kedepannya):**
   - Jika nanti Anda membutuhkan fitur "Login User" dan ingin menyimpan *history/riwayat* pengguna secara permanen, barulah Anda menambahkan database PostgreSQL/MySQL dan kembali menggunakan `models.py` Django. Namun untuk versi awal ini, aplikasi Anda 100% aman, ringan, dan **Stateless**.
