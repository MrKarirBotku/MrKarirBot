# MrKarirBot

MrKarirBot adalah AI Career Assistant untuk membantu pencari kerja Indonesia menemukan karier impian bersama AI.

## Phase 1: Telegram Bot Enterprise

Implementasi Phase 1 mencakup backend FastAPI, Telegram Bot API dengan session state, model database inti, migration Alembic, authentication JWT, RBAC dependency, password hashing, rate limiting, layanan AI, Docker Compose, dan test dasar.


## Roadmap Aktif

Roadmap aktif saat ini terdiri dari 2 phase:

1. **Phase 1: Telegram Bot Enterprise**.
2. **Phase 2: Website Dashboard**.

WhatsApp Business API tidak termasuk roadmap aktif sementara waktu. Detail roadmap tersedia di `docs/ROADMAP.md`.

## Struktur Folder

- `app/main.py`: factory FastAPI dan middleware rate limiter.
- `app/api/v1`: REST API versi 1 untuk health, AI, auth, jobs, dan Telegram webhook.
- `app/core`: konfigurasi dan keamanan.
- `app/database`: koneksi database async SQLAlchemy, model, dan repository.
- `app/database/models`: model PostgreSQL inti untuk user, profile, jobs, bookmark, tracker lamaran, dan audit log.
- `app/services`: business logic AI dan lowongan.
- `app/bot`: handler, keyboard, state, webhook, dan bootstrap Telegram Bot.
- `tests`: unit/API tests.
- `docs`: dokumentasi arsitektur, struktur, roadmap, dan deployment.

Struktur lengkap tersedia di `docs/STRUCTURE.md`.

## Menjalankan Lokal

```bash
cp .env.example .env
docker compose up --build
```

API tersedia di `http://localhost:8000`; Swagger di `/docs`.

## Menjalankan Test

```bash
pip install -e '.[dev]'
pytest
ruff check .
```

## Deployment

1. Set environment variable dari `.env.example` di Railway/Render/VPS.
2. Jalankan container API dengan command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3. Jalankan migration dengan `alembic upgrade head`.
4. Gunakan PostgreSQL managed database dan Redis managed cache.
5. Jangan commit token Telegram/OpenAI; simpan di secret manager platform deployment. Jika token pernah dibagikan di chat, rotasi token melalui BotFather sebelum production.
6. Atur webhook Telegram dengan `python scripts/set_telegram_webhook.py` setelah `TELEGRAM_BOT_TOKEN` dan `TELEGRAM_WEBHOOK_URL` tersedia sebagai environment variable.
7. Untuk mode polling lokal, jalankan `python scripts/run_telegram_polling.py`.
