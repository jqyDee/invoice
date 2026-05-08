from pathlib import Path

from app.models import InvoiceDB, PatientDB
from app.utilities import CACHE_DIR


def generate_invoice_path(invoice: InvoiceDB) -> Path:
    return CACHE_DIR / f"{invoice.invoice_number}.pdf"


def generate_therapy_path(patient: PatientDB) -> Path:
    return CACHE_DIR / f"{patient.patient_id}-{patient.label}-therapy.pdf"


def generate_privacy_path(patient: PatientDB) -> Path:
    return CACHE_DIR / f"{patient.patient_id}-{patient.label}-privacy.pdf"
