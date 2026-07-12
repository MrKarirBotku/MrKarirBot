# Arsitektur MrKarirBot Phase 1

## Komponen

1. **FastAPI Backend**: REST API untuk health check dan modul AI.
2. **Telegram Bot**: menu inline profesional untuk lowongan, AI karier, ATS review, dan interview coach.
3. **PostgreSQL**: penyimpanan user, job, audit log, dan data phase berikutnya.
4. **Redis**: rate limit, session, dan queue readiness.
5. **OpenAI Service**: adapter AI terisolasi agar mudah diganti atau diuji.

## Prinsip

- Clean Architecture ringan: API/Telegram hanya memanggil service layer.
- Security by default: JWT, hashing password, rate limiter, validasi Pydantic.
- Modular: setiap domain dipisahkan di `models`, `schemas`, `services`, dan `api`.

## Flow Telegram

`/start` → Inline Main Menu → Callback Query → Instruksi fitur → User Text → AIService → Reply.
