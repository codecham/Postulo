from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.core.middleware import (
    API_CONTENT_SECURITY_POLICY,
    API_SECURITY_HEADERS,
    BodySizeLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.routes import (
    applications,
    auth,
    cv_imports,
    educations,
    experiences,
    health,
    job_matches,
    job_search,
    profile,
    tracking,
    users,
)

ROUTERS = (
    health.router,
    auth.router,
    users.router,
    profile.router,
    cv_imports.router,
    experiences.router,
    educations.router,
    job_search.router,
    job_matches.router,
    applications.options_router,
    applications.router,
    tracking.board_router,
    tracking.router,
)


def create_app(settings: Settings) -> FastAPI:
    configure_logging(settings)
    # In production the interactive docs are off: they map every route for an attacker.
    # The schema is still exported by `make api-types`, which calls app.openapi() directly.
    docs_enabled = not settings.is_production
    app = FastAPI(
        title=settings.app_name,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )
    add_middlewares(app, settings)
    for router in ROUTERS:
        app.include_router(router)
    return app


def add_middlewares(app: FastAPI, settings: Settings) -> None:
    """Add the middlewares. The last one added runs first on each request."""
    # Let browser code served from another origin call the API. In this project only the
    # Next.js server calls the API, so production can leave the list empty.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    headers = dict(API_SECURITY_HEADERS)
    if settings.is_production:
        headers["Content-Security-Policy"] = API_CONTENT_SECURITY_POLICY
    app.add_middleware(SecurityHeadersMiddleware, headers=headers)
    app.add_middleware(BodySizeLimitMiddleware, max_bytes=settings.max_request_bytes)
    app.add_middleware(RequestLoggingMiddleware)


app = create_app(get_settings())
