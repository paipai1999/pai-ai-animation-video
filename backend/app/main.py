import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api.routes import jobs, styles, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    await init_db()
    print("Database tables initialized.")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Fullstack AI Video Animation Remake Engine powered by Gemini 2.5 Flash & Veo/Pollinations/LTX",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "Accept-Ranges", "Content-Length", "Content-Type"],
)

# Static file serving for local storage assets (outputs, frames, audio)
app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")

# Include Routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(styles.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": "AI Video Animation Remake API is running",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }
