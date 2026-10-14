"""FastAPI application entry point."""
import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import analyses, auth, documents
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.database import Base, engine
from app.services.retention import sweep_loop

configure_logging()
log = logging.getLogger("app.request")
settings = get_settings()

# Multipart framing adds a little overhead on top of the file itself.
_MULTIPART_OVERHEAD = 64 * 1024


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    task = asyncio.create_task(sweep_loop()) if settings.retention_sweep_enabled else None
    yield
    if task:
        task.cancel()


app = FastAPI(
    title="Secure Document and Resume Analysis API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if settings.environment == "prod" else "/docs",
    redoc_url=None,
    openapi_url=None if settings.environment == "prod" else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = uuid.uuid4().hex[:12]
    started = time.perf_counter()

    declared = request.headers.get("content-length", "")
    limit = get_settings().max_upload_bytes + _MULTIPART_OVERHEAD
    if declared.isdigit() and int(declared) > limit:
        response = JSONResponse({"detail": "Request body is too large."}, status_code=413)
    else:
        try:
            response = await call_next(request)
        except Exception as exc:  # log the type only: messages can contain user data
            log.error("id=%s unhandled %s", request_id, type(exc).__name__)
            response = JSONResponse({"detail": "Internal server error"}, status_code=500)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; frame-ancestors 'none'"
        if request.url.path not in {"/docs", "/openapi.json"}
        else "default-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; img-src 'self' data: https://fastapi.tiangolo.com"
    )
    log.info(
        "id=%s %s %s -> %d (%.0f ms)",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - started) * 1000,
    )
    return response


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(analyses.router)
