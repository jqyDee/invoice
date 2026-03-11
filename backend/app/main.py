from fastapi import FastAPI

from .utilities.database import engine
from .models import Base
from fastapi.middleware.cors import CORSMiddleware

from .utilities.router_include import auto_include_routers

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register all routers automatically
auto_include_routers(app)
