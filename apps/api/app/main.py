from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
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

settings = get_settings()

app = FastAPI(title=settings.app_name)

# Let browser code served from another origin (e.g. the frontend) call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(profile.router)
app.include_router(cv_imports.router)
app.include_router(experiences.router)
app.include_router(educations.router)
app.include_router(job_search.router)
app.include_router(job_matches.router)
app.include_router(applications.options_router)
app.include_router(applications.router)
app.include_router(tracking.board_router)
app.include_router(tracking.router)
