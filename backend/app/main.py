from fastapi import FastAPI

from .utilities.database import engine
from .models import Base
from fastapi.middleware.cors import CORSMiddleware

from .utilities.router_include import auto_include_routers

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


# Register all routers automatically
auto_include_routers(app)
