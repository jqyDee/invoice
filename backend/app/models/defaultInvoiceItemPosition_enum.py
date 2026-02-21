import enum


class DefaultInvoiceItemPosition(enum.Enum):
    APPEND = "APPEND"
    PREPEND = "PREPEND"
    BOTH = "BOTH"  # do not know if needed but will keep this for now
