# Deployment Guide

## Docker Compose

```bash
cp .env.example .env
docker compose up -d --build
```

## Production Checklist

- Ganti `SECRET_KEY` dengan nilai acak kuat.
- Isi `TELEGRAM_BOT_TOKEN` dan `OPENAI_API_KEY`.
- Gunakan PostgreSQL dan Redis production managed.
- Aktifkan HTTPS melalui Nginx atau platform PaaS.
- Jalankan backup database harian.
- Pantau log API, Telegram bot, dan audit log.


## Telegram Webhook

Set environment variable `TELEGRAM_BOT_TOKEN` dan `TELEGRAM_WEBHOOK_URL`, lalu jalankan:

```bash
python scripts/set_telegram_webhook.py
```

Token tidak boleh ditulis ke repository atau log publik. Jika token pernah dibagikan di chat, rotasi token melalui BotFather sebelum production.
