import importlib
import pkgutil

from fastapi import APIRouter, FastAPI

from app import routers


def auto_include_routers(fastapi_app: FastAPI):
    """
    Scans the 'routers' package and includes all objects named 'router'.
    """
    for loader, module_name, is_pkg in pkgutil.iter_modules(routers.__path__):
        full_module_name = f"app.routers.{module_name}"

        module = importlib.import_module(full_module_name)

        if hasattr(module, "router") and isinstance(module.router, APIRouter):
            fastapi_app.include_router(module.router)
