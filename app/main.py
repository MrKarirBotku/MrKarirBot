from fastapi import FastAPI, Request

app = FastAPI(
    title="MrKarirBot API",
    version="1.0.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    """Memeriksa apakah API berjalan."""
    return {
        "status": "online",
        "service": "MrKarirBot API",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Endpoint pemeriksaan kesehatan aplikasi."""
    return {"status": "healthy"}


@app.post("/api/v1/telegram/webhook")
async def telegram_webhook(request: Request) -> dict[str, bool]:
    """Menerima update yang dikirim Telegram."""
    update = await request.json()

    # Untuk sementara hanya menampilkan update ke log server.
    print(update)

    return {"ok": True}
