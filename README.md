# Autonomous Discovery Platform

Fondasi layanan otonom yang siap dikembangkan menjadi aplikasi pencari tren
terbaru. Repositori ini sudah menyiapkan API publik untuk mengumpulkan top item
yang sedang viral dari berbagai sumber gratis tanpa perlu konfigurasi manual.

## Fitur Utama

- **Endpoint `/trending`** menggabungkan data populer dari Reddit, Hacker News,
  dan GitHub (dapat diperluas). Jumlah item bawaan adalah 10 namun bisa diatur
  melalui parameter query atau variabel lingkungan.
- **Caching otomatis & pembaruan periodik** menjaga data tetap segar tanpa beban
  permintaan berulang ke sumber eksternal.
- **Monitoring self-healing** melalui modul automation yang siap memperbarui
  cache jika sumber data mengalami gangguan.
- **Struktur modular** memudahkan penambahan sumber data baru, penyimpanan,
  maupun antarmuka pengguna.

## Struktur Direktori

```
.
├── automation/                    # Rutin otomatisasi & self-healing
│   └── self_healing/              # Monitor siap pakai untuk trending service
│       └── monitor.py
├── backend/
│   ├── app/
│   │   ├── core/                  # Konfigurasi dan utilitas global
│   │   ├── services/
│   │   │   └── trending/          # Aggregator & sumber data viral
│   │   ├── routers/               # Endpoint FastAPI
│   │   └── main.py                # Entry point + lifecycle background jobs
│   ├── requirements.txt
│   └── tests/                     # Unit test untuk service trending
├── docs/
│   └── ARCHITECTURE.md            # Dokumentasi arsitektur & roadmap
├── infra/
│   ├── docker-compose.yaml
│   └── dockerfiles/
│       └── api.Dockerfile
├── scripts/
│   ├── dev-down.sh
│   └── dev-up.sh
└── README.md
```

## Menjalankan Secara Lokal

1. Pasang dependensi Python backend:
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Jalankan API:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Buka dokumentasi interaktif di `http://localhost:8000/docs` untuk mencoba
   endpoint `/trending` dan `/status/health`.

> Alternatif: gunakan `scripts/dev-up.sh` untuk menjalankan via Docker
> Compose, dan `scripts/dev-down.sh` untuk mematikannya.

## Konfigurasi

Semua konfigurasi bisa dilakukan melalui variabel lingkungan (prefiks `APP_`):

| Variabel | Default | Deskripsi |
| --- | --- | --- |
| `APP_TRENDING_DEFAULT_LIMIT` | `10` | Jumlah item trending ketika parameter `limit` tidak diberikan. |
| `APP_TRENDING_REFRESH_SECONDS` | `900` | Interval refresh cache (detik). |
| `APP_TRENDING_SOURCES` | `reddit,hackernews,github` | Daftar sumber aktif, dapat ditambah misal `reddit,youtube`. |
| `APP_HTTP_TIMEOUT_SECONDS` | `10` | Timeout request HTTP ke sumber eksternal. |

Konfigurasi juga bisa dimasukkan ke file `.env` di folder `backend/`.

## Rencana Pengembangan

- Tambahkan penyimpanan historis (mis. PostgreSQL) untuk analitik tren.
- Integrasikan sumber data lain seperti TikTok, YouTube, atau marketplace lokal
  menggunakan pola adapter yang sama.
- Kembangkan antarmuka visual di folder `frontend/` untuk menampilkan dashboard
  real-time.
- Implementasikan workflow self-healing lanjutan dengan scheduler dan notifikasi
  ketika sumber data gagal.

Semua dependensi menggunakan software open-source/gratis sehingga tidak ada
biaya lisensi tambahan.
