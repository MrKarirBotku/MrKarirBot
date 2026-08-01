# Deployment Guide

## Docker Compose

> **Peringatan:** dependency container dan health check sudah dikonfigurasi, tetapi repository belum
> memiliki baseline schema lengkap. Fresh database belum dapat menjalankan API lowongan sampai
> baseline Supabase direkonstruksi. Jangan gunakan Compose sebagai bukti production readiness.

```bash
cp .env.example .env
docker compose up -d --build
```

## Production Checklist

- Ganti `SECRET_KEY` dengan nilai acak minimal 48 karakter.
- Isi `TELEGRAM_BOT_TOKEN` dan `OPENAI_API_KEY`.
- Isi `TELEGRAM_WEBHOOK_SECRET`; webhook akan gagal tertutup jika secret kosong.
- Gunakan `https://mrkarirai.web.id` untuk `SITE_URL` dan `APP_URL` production.
- Isi `SUPABASE_URL` dan `SUPABASE_PUBLISHABLE_KEY`.
- Gunakan PostgreSQL dan Redis production managed.
- Aktifkan HTTPS dan origin protection melalui Cloudflare/Railway.
- Jalankan backup database harian.
- Pantau log API, Telegram bot, dan audit log.


## Telegram Webhook

Set environment variable `TELEGRAM_BOT_TOKEN` dan `TELEGRAM_WEBHOOK_URL`, lalu jalankan:

```bash
python scripts/set_telegram_webhook.py
```

Token tidak boleh ditulis ke repository atau log publik. Jika token pernah dibagikan di chat, rotasi token melalui BotFather sebelum production.
