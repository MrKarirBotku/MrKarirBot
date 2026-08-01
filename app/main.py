import logging
from pathlib import Path
from time import perf_counter
from urllib.parse import urljoin
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")
    web_dir = Path(__file__).resolve().parent.parent / "web"
    limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    app.include_router(api_router)
    app.mount("/assets", StaticFiles(directory=web_dir), name="assets")

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        started_at = perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id[:128]
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if settings.environment.casefold() == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        logging.getLogger("mrkarirbot.request").info(
            "request_complete method=%s path=%s status=%s duration_ms=%s request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            round((perf_counter() - started_at) * 1000, 2),
            request_id[:128],
        )
        return response

    @app.get("/", include_in_schema=False)
    async def website() -> FileResponse:
        return FileResponse(web_dir / "index.html")

    @app.get("/robots.txt", include_in_schema=False)
    async def robots() -> PlainTextResponse:
        sitemap_url = urljoin(f"{settings.site_url.rstrip('/')}/", "sitemap.xml")
        return PlainTextResponse(f"User-agent: *\nAllow: /\nSitemap: {sitemap_url}\n")

    @app.get("/sitemap.xml", include_in_schema=False)
    async def sitemap() -> Response:
        root = settings.site_url.rstrip("/")
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"<url><loc>{root}/</loc></url>"
            "</urlset>"
        )
        return Response(body, media_type="application/xml")

    @app.get("/manifest.webmanifest", include_in_schema=False)
    async def manifest() -> JSONResponse:
        return JSONResponse(
            {
                "name": "MrKarir AI",
                "short_name": "MrKarir",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#f7f9fc",
                "theme_color": "#0b5cff",
                "lang": "id",
            },
            media_type="application/manifest+json",
        )

    @app.get("/ads.txt", include_in_schema=False)
    async def ads_txt() -> PlainTextResponse:
        return PlainTextResponse(settings.ads_txt_content, media_type="text/plain")

    return app


app = create_app()
