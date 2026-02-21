import enum


class InvoiceStatus(enum.Enum):
    DRAFT = "DRAFT"
    SAVED = "SAVED"
    PAYMENT_DUE = "PAYMENT_DUE"
    PAID = "PAID"