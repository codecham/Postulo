from fastapi import FastAPI

from app.core.config import get_settings
from app.routes import auth, health, users

app = FastAPI(title=get_settings().app_name)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
