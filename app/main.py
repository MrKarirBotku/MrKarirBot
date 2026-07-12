from fastapi import FastAPI
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from app.api.v1.router import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")
    limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    app.include_router(api_router)
    return app


app = create_app()
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
