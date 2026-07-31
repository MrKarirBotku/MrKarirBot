# MrKarirBot

MrKarirBot adalah AI Career Assistant untuk membantu pencari kerja Indonesia menemukan karier impian bersama AI.

## MVP Website + Telegram Otomatis

MrKarirBot menggunakan satu backend dan satu database untuk melayani website publik, bot Telegram,
dan channel Telegram. Worker mengambil lowongan asli dari API publik, menormalkan data, menghapus
duplikasi, menyimpannya ke PostgreSQL/Supabase, lalu memublikasikan lowongan baru ke channel.

Sumber MVP:

- Remotive untuk lowongan remote. Semua lowongan mempertahankan atribusi dan tautan Remotive.
- Arbeitnow untuk lowongan Eropa dan remote.

Data contoh tidak digunakan sebagai lowongan produksi.


## Roadmap Aktif

Roadmap aktif saat ini terdiri dari 3 phase:

1. **MVP: website, bot, agregator, dan channel otomatis**.
2. **Akun pengguna, bookmark, tracker, dan notifikasi personal**.
3. **CV ATS, interview AI, rekomendasi karier, dan dashboard admin lanjutan**.

WhatsApp Business API tidak termasuk roadmap aktif sementara waktu. Detail roadmap tersedia di `docs/ROADMAP.md`.

## Struktur Folder

- `app/main.py`: factory FastAPI dan middleware rate limiter.
- `app/api/v1`: REST API versi 1 untuk health, AI, auth, jobs, dan Telegram webhook.
- `app/core`: konfigurasi dan keamanan.
- `app/database`: koneksi database async SQLAlchemy, model, dan repository.
- `app/database/models`: model PostgreSQL inti untuk user, profile, jobs, bookmark, tracker lamaran, dan audit log.
- `app/services`: business logic AI dan lowongan.
- `app/sources`: adapter sumber lowongan asli.
- `app/workers/jobs.py`: sinkronisasi dan publikasi channel terjadwal.
- `app/bot`: handler, keyboard, state, webhook, dan bootstrap Telegram Bot.
- `web`: website publik responsif.
- `tests`: unit/API tests.
- `docs`: dokumentasi arsitektur, struktur, roadmap, dan deployment.

Struktur lengkap tersedia di `docs/STRUCTURE.md`.

## Menjalankan Lokal

```bash
cp .env.example .env
docker compose up --build
```

API tersedia di `http://localhost:8000`; Swagger di `/docs`.

Jalankan worker otomatis pada terminal kedua:

```bash
python scripts/run_job_worker.py
```

## Menjalankan Test

```bash
pip install -e '.[dev]'
pytest
ruff check .
```

## Deployment

1. Simpan seluruh nilai `.env.example` sebagai environment variable/secret platform.
2. Jalankan migration sekali dengan `alembic upgrade head`.
3. Buat service web dengan command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. Buat service worker dari repo yang sama dengan command `python scripts/run_job_worker.py`.
5. Isi `TELEGRAM_CHANNEL_ID=@MrKarirAI` dan jadikan bot sebagai admin channel.
6. Isi `TELEGRAM_WEBHOOK_SECRET` dengan nilai acak, lalu jalankan `python scripts/set_telegram_webhook.py`.
7. Jangan commit token atau key. Simpan semuanya di secret manager platform deployment.
8. Untuk polling bot saat pengembangan lokal, jalankan `python scripts/run_telegram_polling.py`.

Endpoint utama:

- `GET /api/v1/jobs?q=customer+support&remote=true`
- `GET /api/v1/jobs/{id}`
- `POST /api/v1/jobs/sync/run` (admin)
- `POST /api/v1/jobs/publish/run` (admin)
- `POST /api/v1/telegram/webhook`
