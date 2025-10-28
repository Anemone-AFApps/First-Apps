# Autonomous First App

Fondasi untuk platform aplikasi otonom yang dapat dikembangkan menjadi layanan
multi-fitur. Struktur repository ini dibuat modular sehingga mudah menambah
komponen baru seperti API tambahan, integrasi pihak ketiga, maupun modul
self-healing.

## Struktur Direktori

```
.
├── automation/            # Rutin otomatisasi & self-healing
│   └── self_healing/
│       └── monitor.py
├── backend/               # Layanan inti berbasis FastAPI
│   ├── app/
│   │   ├── main.py
│   │   └── routers/
│   │       └── status.py
│   └── requirements.txt
├── docs/                  # Dokumentasi arsitektur & panduan
│   └── ARCHITECTURE.md
├── infra/                 # Konfigurasi deployment (Docker, dsb.)
│   ├── docker-compose.yaml
│   └── dockerfiles/
│       └── api.Dockerfile
├── scripts/               # Skrip utilitas untuk pengembangan
│   ├── dev-down.sh
│   └── dev-up.sh
└── README.md
```

## Cara Menjalankan (Lokal)

1. Pastikan Docker dan Docker Compose tersedia.
2. Jalankan `scripts/dev-up.sh` untuk menyalakan layanan API.
3. Akses dokumentasi interaktif di `http://localhost:8000/docs`.
4. Gunakan `scripts/dev-down.sh` untuk mematikan layanan.

## Arah Pengembangan

- **Integrasi API eksternal**: Tambahkan client SDK atau modul integrasi di
  `backend/app/routers/` atau `automation/` sesuai kebutuhan.
- **Penyimpanan data**: Deklarasikan service database di `infra/` dan buat layer
  repository di backend.
- **Antarmuka pengguna**: Tambahkan folder `frontend/` atau `apps/` untuk
  aplikasi web/mobile, lalu hubungkan ke API.
- **Self-healing lanjutan**: Implementasikan monitor tambahan di
  `automation/self_healing/` untuk melakukan remediasi otomatis berdasarkan
  metrik.

Semua komponen menggunakan tool dan library open-source sehingga tidak ada biaya
lisensi.
