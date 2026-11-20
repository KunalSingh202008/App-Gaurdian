"""Vercel entrypoint for the Studio API and compiled web frontend."""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi.concurrency import run_in_threadpool
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("STUDIO_GENERATION_DRIVER", "request")
sys.path.insert(0, str(ROOT / "services" / "api"))

from db import migrate
from main import app


@asynccontextmanager
async def lifespan(_app):
    await run_in_threadpool(migrate)
    yield


app.router.lifespan_context = lifespan
app.mount("/", StaticFiles(directory=ROOT / "public", html=True), name="studio")
