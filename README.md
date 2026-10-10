# Build Data Staging csv menjadi json Database

mengubah CSV mentah hasil scraping menjadi database hardware, mengubah lembar uji manual
menjadi sampel terstruktur dimana data tersebut menjadi bahan baku kalibrasi performa ShaderBench

## 🌟 Apa itu ShaderBench?
[ShaderBench](https://ShaderBench.com) adalah alat analisis performa dan rekomendasi setting Minecraft berbasis web. Alih-alih hanya memberikan tebakan, aplikasi ini menggunakan pendekatan provenance-first (jujur terhadap asal-usul data) dan model fisika satu-skalar yang dipadukan dengan Machine Learning (Random Forest).

---

### 🛠️ Komponen Utama

| Skrip | Peran | Input | Output |
|---|---|---|---|
| `build_database_soc.py` | Kamus SoC mobile (Android + iOS) | `data/staging/benchmark_soc.csv`, `data/raw/details_cache.json` | `data/db/database_soc.json` |
| `build_database_gpu.py` | Kamus GPU PC (desktop + laptop) | `data/staging/benchmark_pc_gpu.csv` | `data/db/database_gpu.json` |
| `build_database_cpu.py` | Kamus CPU PC (desktop + laptop) | `data/staging/benchmark_pc_cpu.csv` | `data/db/database_cpu.json` |

---

> | Repo | URL | Peran |
> |---|---|---|
> | **scraper** (ini) | [`Scraper`](https://github.com/wansobriamin/scraper-data-gpu-cpu-soc) | Scrape benchmark mentah |
> | **convert** | [`convert`](https://github.com/wansobriamin/normalize-convert-raw-to-staging) | Skor mentah → `gpu_index`/`cpu_index` (CSV staging) |
> | **build** | [`build`](https://github.com/wansobriamin/build-csv-to-json-benchmark-device) | mengubah data CSV staging menjadi file database `.json`  |


## CLI

Jalankan dari root backend

```bash
# 1) siapkan CSV staging

# 2) bangun database hardware
python -m build.build_soc_database
python -m build.build_gpu_database
python -m build.build_cpu_database

```

## Workflow

```text
        [Scraper eksternal]
                │  CSV mentah benchmark
                ▼
        data/staging/*.csv ──► build_soc_database.py   ──► data/db/soc_database.json
                           ├──► build_gpu_database.py  ──► data/db/gpu_database.json
                           └──► build_cpu_database.py  ──► data/db/cpu_database.json
```


---

## Etika & Lisensi

- kode ini bertugas mengubah data mentah hasil scraper menjadi data bersih
  mengagregasi untuk riset pribadi dan pengembangan ShaderBench.
- Kode ini disediakan apa adanya (as-is) untuk tujuan edukasi.

Copyright (c) 2026 wansobriamin
