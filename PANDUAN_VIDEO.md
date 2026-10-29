# Panduan Video Affiliate Elora Fashion

Aturan dari Soom: **sebelum membuat video baru, riset dulu musik dan gaya editan yang sedang efektif.** Panduan ini adalah hasil riset 26 Okt 2026. Perbarui setiap kali riset ulang.

## Gaya editan (hasil riset)
- **Durasi:** 8–15 detik untuk produk di bawah Rp500 ribu. Video pendek yang ditonton sampai habis lebih laku.
- **Ganti adegan setiap 2–3 detik**, jangan slide statis. Gunakan zoom/punch-in yang pas dengan ketukan musik.
- **Hook 1–3 detik pertama:** pernyataan yang menantang, masalah yang relatable ("Celana kerja cepat kusut?"), atau hasil dulu. **Jangan** buka dengan logo atau nama merek.
- **Teks overlay:** maksimal 8–10 kata per layar, tampil minimal 2–3 detik, kontras tinggi, di 60% bagian atas layar. Tulis manfaat yang spesifik, bukan klaim umum.
- **Format yang paling laku:** masalah → solusi, perbandingan atau split-screen, kompilasi beberapa produk ("3 celana kerja di bawah 150rb"), dan tutorial padu padan.
- **Hindari terlihat seperti katalog atau stok foto**, karena bisa menurunkan kepercayaan dan jangkauan. Rekaman asli (tangan, unboxing) jauh lebih baik.

## Musik dan suara
- Yang paling efektif: **voice-over + lagu trending pelan (20–30%)**. Lebih baik daripada musik saja.
- Pilih sound trending yang **belum terlalu ramai** (kurang dari ±50 ribu pemakaian).
- **Lagu trending tidak bisa ditanam di file video** karena hak cipta. Harus ditambahkan dari pustaka musik TikTok di aplikasi.
- Kalau memakai suara AI atau TTS, beri label **"Konten AI"** saat upload.

## Batasan teknis saat ini
- Fitur musik otomatis lewat Repliz tidak berjalan di akun TikTok ini, dan daftar musik trending dari Repliz kosong.
- Workspace tidak punya TTS (voice-over AI) yang bisa dipakai.
- Opsi terbaik: kirim video ke TikTok sebagai **draf**, lalu Soom memilih lagu trending di aplikasi (±1 menit), atau Soom merekam voice-over 10–15 detik.

## Sumber
- https://pixelpanda.ai/blog/2026/03/30/tiktok-shop-product-videos-2026/
- https://www.industry.co.id/read/155846/konten-tiktok-affiliate-tanpa-wajah-2026-strategi-cuan-dari-kamera-belakang
- https://creativedisc.com/2026/08/10-lagu-yang-viral-di-tiktok-sepanjang-2026-dari-die-on-this-hill-hingga-mmg-my-mine-gue/

## Template yang dipakai sejak 26 Okt 2026 (tools/render3.py)
- Total ±8,5 detik, 112 BPM, ganti adegan setiap 3 ketukan (±1,6 detik), CTA 4 ketukan.
- Adegan 1 berisi hook berupa pertanyaan masalah, teks kuning besar dengan efek getar ringan.
- Setiap potongan diberi punch-in zoom dan flash putih tipis. Teks berada di bagian atas, foto produk di atas latar blur penuh layar.
- Hasil awal (25 Okt, template lama 15 detik): ±200 tontonan, tapi rata-rata hanya ditonton 1,5–2,5 detik. Evaluasi template baru setelah tayang.

## Aturan musik (28 Okt 2026)
- **Jangan pakai lagi musik buatan sendiri (beat.py/beat2.py).** Soom menilai musiknya berulang, tidak bagus, dan mengganggu.
- **TikTok dan YouTube**: render video **tanpa musik**, kirim sebagai **draf** (TikTok: isDraft, masuk Kotak Masuk; YouTube: privat), lalu Soom menambahkan lagu sendiri di aplikasi. Mode draf TikTok terbukti berhasil 28 Okt (postId INBOX_TIKTOK).
- Kalau daftar musik trending Repliz sudah terisi, pasang ID lagu TikTok lewat additionalInfo.music.

## Ide format foto-slideshow fashion (riset 29 Okt 2026)
- Daftar bernomor ("3 gaya pakai 1 celana"), satu foto per gaya, 1,5–2 detik per slide.
- Fit check: tinggi dan ukuran di teks, supaya pembeli bisa menilai ukurannya.
- Satu celana dipadu atasan berbeda untuk momen berbeda (kerja, jalan, malam).
- Sumber: https://ecomdymedia.com/blog/5-high-converting-tiktok-creative-ideas-for-fashion-brands-in-2026
