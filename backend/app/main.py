"""FastAPI application: wiring, CORS, error handlers, startup cache load."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import accuracy, forecasts, health
from app.config import get_settings
from app.data.cache import get_cache
from app.errors import ApiError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    get_cache().load(settings.data_dir)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Wind Forecast & Accuracy Portal",
        description="Day-ahead UK wind generation forecast visibility and accuracy analysis.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.exception_handler(ApiError)
    async def _handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=exc.to_body())

    @app.exception_handler(RequestValidationError)
    async def _handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {"loc": list(e.get("loc", [])), "msg": e.get("msg", ""), "type": e.get("type", "")}
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "INVALID_PARAMETER",
                    "message": "Invalid or missing request parameter(s).",
                    "details": {"errors": details},
                }
            },
        )

    app.include_router(health.router, prefix="/api")
    app.include_router(forecasts.router, prefix="/api")
    app.include_router(accuracy.router, prefix="/api")
    return app


app = create_app()
