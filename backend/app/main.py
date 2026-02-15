import importlib
import pkgutil

from fastapi import FastAPI, APIRouter

from . import routers
from .utilities.database import engine
from .models import Base
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

# TODO: change this to be less accessive
app = FastAPI(
    servers=[
        {"url": "http://localhost:8000", "description": "Local development server"},
    ]
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def auto_include_routers(fastapi_app: FastAPI):
    """
    Scans the 'routers' package and includes all objects named 'router'.
    """
    for loader, module_name, is_pkg in pkgutil.iter_modules(routers.__path__):
        full_module_name = f"app.routers.{module_name}"

        module = importlib.import_module(full_module_name)

        if hasattr(module, "router") and isinstance(module.router, APIRouter):
            fastapi_app.include_router(module.router)


# Register all routers automatically
auto_include_routers(app)
