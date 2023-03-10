from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from auth.api.api import api_router
from auth.core.config import settings
from auth.db.init_db import init_db
from auth.db.session import SessionLocal
import subprocess

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


@app.on_event("startup")
def on_startup():
    subprocess.run(["alembic", "upgrade", "head"])
    db = SessionLocal()
    init_db(db)


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin)
                       for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
