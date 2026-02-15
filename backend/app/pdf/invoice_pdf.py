from fpdf import FPDF, XPos, YPos
from ..utilities.config import LOGO_PATH
from ..models import InvoiceDB, SettingsDB


class InvoicePdf(FPDF):
    """
    overwrites the default FPDF2 header and footer functions for KG Rechnung.
    HIDE_PHYSIO: Only for HP invoices. Hides the Physiotherapie badge
    """

    def __init__(
            self,
            invoice: InvoiceDB,
            settings: SettingsDB,
            hide_physio: bool
    ):
        super().__init__()

        self.set_title(f"{invoice.invoice_number}")

        self.invoice_number = invoice.invoice_number
        self.tax_id = settings.tax_id
        self.iban = settings.iban
        self.bic = settings.bic
        self.hide_physio = hide_physio

    def header(self):
        """New PDF header section"""

        # Logo
        try:
            self.image(
                x=22,
                y=17,
                name=LOGO_PATH,
                w=18,
                alt_text="Logo",
            )
        except FileNotFoundError:
            pass
        self.set_font("helvetica", "B", 14)
        self.cell(0, new_x=XPos.LMARGIN, new_y=YPos.TMARGIN)
        self.ln(2.5)
        self.cell(25)
        self.cell(0, text="Mervi Fischbach", align="L")
        self.ln()
        self.cell(25)
        self.set_font("helvetica", "B", 12)
        self.set_text_color(150)
        self.cell(0, text="Heilpraktikerin &", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(25)
        # hide Physiotherapy on HP Invoices
        if self.hide_physio:
            self.set_text_color(255)
        self.cell(0, text="Physiotherapeutin")
        self.ln(23)

    # Page footer
    def footer(self):
        """New PDF footer section"""

        # Position at 3.5 cm from bottom
        self.set_y(-35)
        # helvetica italic 8
        self.set_font("helvetica", "B", 8)
        self.cell(0, 5, "Bankverbindung", align="C")
        self.ln(3)
        self.cell(0, 5, f"IBAN: {self.iban}", align="C")
        self.ln(3)
        self.cell(0, 5, f"BIC: {self.bic}", align="C")
        self.ln(3)
        self.set_font("helvetica", "", 6)
        self.cell(1, 5, f"Rechnungsnummer: {self.invoice_number}", align="L")
        self.cell(0, 5, f"Steuer Nummer: {self.tax_id} - Ust. Befreit nach §4 UStG", align="C")
        # Page number
        self.cell(0, 5, "Seite " + str(self.page_no()) + " von {nb}", align="R")
