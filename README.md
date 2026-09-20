# Portofolio Winodya Zenitha

Halaman portofolio satu halaman. Kode ada di `index.html`, semua teks ada di `content.json`, dan semua gambar ada di `assets/`. Waktu halaman dibuka, isinya dibaca dari `content.json`, jadi untuk menambah project, mengganti foto, atau mengubah teks kamu tidak perlu menyentuh HTML, CSS, atau JavaScript.

Situsnya di-host di Amazon S3 dengan CloudFront di depannya. Infrastrukturnya ditulis dengan Terraform, dan setiap push ke branch `main` langsung di-deploy oleh GitHub Actions lewat OIDC.

## Isi repo

```
.
├── site/                       yang di-upload ke S3
│   ├── index.html              kode halaman (HTML, CSS, JavaScript, GSAP)
│   ├── content.json            semua teks, link, dan path gambar
│   └── assets/                 semua gambar
├── infra/                      Terraform: S3, CloudFront, OIDC, budget alert
├── scripts/
│   ├── check_content.py        cek content.json sebelum deploy
│   └── smoke_test.py           cek situs live sesudah deploy
└── .github/workflows/
    └── deploy.yml              deploy otomatis setiap push ke main
```

Isi `site/assets/`:

| Folder | Isinya |
|---|---|
| `photos/` | foto profil (bingkai sulur) |
| `projects/` | foto project kuliah dan Bangkit |
| `organization/` | foto organisasi dan kepanitiaan |
| `certificates/` | sertifikat |
| `posters/` | poster design |
| `thesis/` | grafik hasil uji di bagian skripsi |
| `honours/` | foto di kartu prestasi dan publikasi |
| `tools/` | ikon Skills & Tools |
| `decor/` | ornamen dan frame animasi: teratai, koi, kupu-kupu, bingkai foto, air kolam |
| `_unused/` | 12 frame koi lama yang tidak dipakai kode mana pun, tidak ikut di-upload |

## Cara kerja deploy

```
git push ──> GitHub Actions ──(OIDC)──> IAM role ──> S3 (private) ──> CloudFront (HTTPS) ──> pengunjung
```

- **Tanpa access key.** Di laptop, AWS CLI dan Terraform login lewat `aws login`. GitHub Actions memakai OIDC, dan role-nya hanya bisa dipakai oleh branch `main` di repo ini. Repo dicocokkan lewat nomor ID akun dan ID repo, bukan cuma nama, jadi kalau suatu saat namanya dipakai orang lain, role ini tetap tidak bisa dipakai.
- **Bucket S3 private.** Satu-satunya yang boleh membaca isinya adalah distribution CloudFront milik situs ini, lewat Origin Access Control.
- **Hak akses seperlunya.** Role deploy cuma boleh menulis ke bucket situs dan mengosongkan cache distribution ini. Tidak ada izin lain.
- **Cache.** Browser menyimpan gambar selama 1 hari. `index.html` dan `content.json` selalu dicek ulang, dan cache CloudFront dikosongkan di setiap deploy.
- **Dicek dua kali.** Sebelum upload, `check_content.py` mengecek JSON dan semua path gambar, termasuk huruf besar/kecilnya (S3 membedakan `Foto.webp` dan `foto.webp`, Windows tidak). Sesudah upload, `smoke_test.py` membuka situs live dan memastikan halaman, JSON, dan gambar terkirim dengan benar.
- **State Terraform** disimpan di S3 dengan locking bawaan, tanpa DynamoDB.
- **Budget alert** mengirim email kalau pemakaian akun bulan ini mendekati batas.

## Update konten

1. Edit `site/content.json`, tambah atau ganti gambar di `site/assets/`.
2. Cek di laptop (lihat bagian berikutnya), lalu jalankan `python scripts/check_content.py site`.
3. Commit dan push ke `main`. Sekitar 1 sampai 2 menit kemudian perubahannya sudah live.

Progres dan hasil deploy bisa dilihat di tab **Actions** di GitHub. Kalau ada yang salah di `content.json`, deploy berhenti sebelum upload, dan pesan errornya menunjukkan bagian mana yang harus diperbaiki.

## Melihat halaman di komputer sendiri

Kalau `index.html` di-double-click, halamannya kosong dan muncul pesan di bawah. Browser memang melarang halaman yang dibuka dari file untuk membaca file lain seperti `content.json`. Solusinya jalankan server lokal kecil:

```bash
cd site
python -m http.server 8000
```

Lalu buka http://localhost:8000. Di Mac atau Linux, perintahnya mungkin `python3`. Kalau pakai VS Code, bisa juga pasang ekstensi **Live Server**, klik kanan `index.html`, lalu pilih *Open with Live Server*.

## Aturan dasar JSON

- Teks selalu diapit tanda kutip dua: `"seperti ini"`.
- Item dalam daftar dipisah koma, tapi item terakhir tidak boleh diikuti koma.
- Kalau teksnya sendiri butuh tanda kutip dua, tulis `\"`.

Kalau ada yang salah tulis, halaman menampilkan kotak pesan berisi nomor baris dan kolom yang bermasalah. Biasanya masalahnya ada di baris itu atau satu baris sebelumnya.

## Tanda khusus di dalam teks

| Tulis di JSON | Hasil di halaman |
|---|---|
| `{Z}enitha` | huruf Z tampil sebagai huruf awal bergaya tulisan tangan, seperti di semua judul |
| `<em>Laut Bercerita</em>` | teks miring |
| `<strong>penting</strong>` | teks tebal |
| `40\u00a0persen` | spasi yang tidak boleh terpotong ke baris baru |

Pengecualian: `about.bio` harus teks biasa tanpa tag, karena kalimatnya dimunculkan kata per kata.

## Menambah project

Salin satu blok di `projects.items`, lalu taruh di posisi yang kamu mau. Urutan di JSON sama dengan urutan kartu di halaman.

```json
{
  "title": "Nama Project",
  "meta": "Mata kuliah · Peran · 2026",
  "images": ["assets/projects/nama-foto.webp"],
  "caption": "Keterangan kecil di bawah foto",
  "paragraphs": ["Paragraf pertama.", "Paragraf kedua."],
  "points": ["Poin pertama", "Poin kedua"],
  "stack": ["Laravel", "MySQL"],
  "link": { "text": "github.com/kamu/repo", "url": "https://github.com/kamu/repo" }
}
```

Semua bagian boleh dihapus kecuali `title`. Kalau `images` berisi lebih dari satu foto, fotonya bergantian sendiri. Bentuk kartu yang sama dipakai di `organization.items`, `bangkit.items`, dan `honours.items`.

## Mengganti foto

Ada dua cara:

1. Upload foto baru dengan nama file baru ke folder yang sesuai di `assets/`, lalu ganti path-nya di `content.json`. Cara ini paling aman karena perubahannya langsung terlihat oleh semua pengunjung.
2. Timpa file lama dengan file baru yang namanya sama persis, tanpa mengubah JSON. Cara ini praktis, tapi pengunjung yang pernah membuka situs bisa masih melihat foto lama sampai 1 hari karena cache browser.

Pakai huruf kecil dan tanda hubung untuk nama file, tanpa spasi. Format `.webp` paling ringan, tapi `.jpg` dan `.png` juga bisa. Rasio yang pas:

- Foto kartu 16:9 dan gambar skripsi 16:10. Kalau rasionya beda, tepi foto terpotong.
- Poster 3:4 dan sertifikat 1:1. Kalau rasionya beda, muncul ruang kosong di sisinya.
- Foto profil sebaiknya tegak (potret), karena bingkainya oval.

## Bagian lain di content.json

| Bagian | Isinya |
|---|---|
| `meta` | judul tab browser dan deskripsi halaman |
| `cover` | nama besar di halaman pembuka dan tulisan "scroll" |
| `about` | nama, peran, bio, pendidikan, dan dua foto profil yang bergantian |
| `skills.tools` | ikon Skills & Tools. Tanpa `icon`, yang tampil dua huruf awal nama. Susunan kerucutnya dirancang untuk 17 ikon, jadi kalau jumlahnya beda jauh, bentuknya ikut berubah |
| `toc` | daftar isi. Angka seperti "6 project" masih ditulis manual |
| `thesis` | bagian skripsi, termasuk dua gambar di `shots` |
| `posters.items` | poster yang berganti sendiri |
| `honours` | prestasi (`items`) dan sertifikat (`certificates`) |
| `contact.links` | tombol Email, LinkedIn, GitHub di bagian penutup |

Soal `meta`: preview link di WhatsApp atau LinkedIn membaca `<title>` dan `<meta name="description">` yang tertulis langsung di `index.html`, bukan dari JSON. Jadi kalau `meta` diubah, samakan juga dua baris itu.

## Yang sengaja tidak diatur dari JSON

Gambar di `assets/decor/` adalah bagian dari desain dan animasi, jadi kodenya memanggil nama file secara langsung. Kalau mau mengganti salah satunya, timpa file dengan nama yang sama. Gambar vektor yang digambar langsung dengan kode (sulur di sekitar foto, amplop, daun teratai, kelopak yang jatuh) tetap ada di `index.html`.
