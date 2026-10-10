# 🗄️ ShaderBench Build — Pipeline Pembangunan Database Hardware

**Kumpulan skrip ETL untuk membangun "kamus spesifikasi" device (SoC, GPU, CPU) yang menjadi fondasi prediksi ShaderBench.**

Repository ini berisi tiga skrip inti yang mengubah data mentah hasil scraping benchmark (Nanoreview, TechPowerUp, dll.) menjadi database JSON terstruktur yang langsung dikonsumsi oleh engine prediksi ShaderBench.

---

## 🎮 Tentang ShaderBench

**ShaderBench** adalah aplikasi web prediktif yang membantu pemain Minecraft (Bedrock/PE) mengetahui apakah device mereka mampu menjalankan shader tertentu dengan lancar. Aplikasi ini menggunakan pendekatan **provenance-first** dengan menggabungkan:

- **Rumus fisika sederhana**: `fps = TARGET_FPS × gpu_index / (shader_load + BASE)`
- **Machine Learning** (Random Forest) untuk klasifikasi kategori performa
- **Koherensi prediksi**: FPS yang ditampilkan selalu sesuai dengan setting yang direkomendasikan
- **Provenance jujur**: setiap angka memiliki asal-usul yang jelas dan ditandai sebagai terukur/proyeksi

**Repository ini adalah hulu (sumber data)** yang menyuplai "kamus" kapasitas hardware (`gpu_index`, `cpu_index`) agar engine ShaderBench dapat mengenali device yang diinput oleh user dan menghitung prediksi FPS secara akurat.

---

## 📁 Struktur Folder
