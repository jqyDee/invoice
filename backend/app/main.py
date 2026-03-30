import logging
from importlib import metadata
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .utilities.database import SessionLocal
from .utilities.router_include import auto_include_routers
from .utilities.seed import seed_users

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()
    yield


try:
    __version__ = metadata.version("invoice-backend")
except metadata.PackageNotFoundError:
    __version__ = "Not found"

logger.info("Invoice backend version: %s", __version__)

app = FastAPI(
    lifespan=lifespan,
    version=__version__
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers automatically
auto_include_routers(app)
