from fastapi import FastAPI
from .utilities.database import engine
from .models import Base
from .routers import patient_router, invoice_router, pdf_router
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
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