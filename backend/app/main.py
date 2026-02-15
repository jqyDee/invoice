import logging

from fastapi import FastAPI
from .utilities.database import engine
from .models import Base
from .routers import patient_router, invoice_router, pdf_router
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

app.include_router(patient_router.router)
app.include_router(invoice_router.router)
app.include_router(pdf_router.router)