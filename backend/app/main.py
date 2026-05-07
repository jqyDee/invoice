import logging
from contextlib import asynccontextmanager
from importlib import metadata

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .utilities.logger_setup import setup_global_logging

setup_global_logging()
logger = logging.getLogger("uvicorn.error")

from .utilities.database import SessionLocal
from .utilities.router_include import auto_include_routers
from .utilities.seed import seed_users

try:
    __version__ = metadata.version("invoice-backend")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "Not found"  # pragma: no cover


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Backend version: %s", __version__)
    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()
    yield


app = FastAPI(lifespan=lifespan, version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers automatically
auto_include_routers(app)
