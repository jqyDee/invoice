from fpdf import FPDF, XPos, YPos

from ..models import InvoiceDB, InvoiceType, SettingsDB
from ..utilities import INVOICE_FOOTER_FONT_SIZE
from ..utilities.config import FONTS_DIR, LOGO_PATH


class InvoicePdf(FPDF):
    """
    overwrites the default FPDF2 header and footer functions for KG Rechnung.
    HIDE_PHYSIO: Only for HP invoices. Hides the Physiotherapie badge
    """

    def __init__(
        self,
        invoice: InvoiceDB,
        settings: SettingsDB,
    ):
        super().__init__()

        self.add_font(family="Roboto", style="", fname=str(FONTS_DIR / "Roboto-Regular.ttf"))

        self.add_font(family="Roboto", style="B", fname=str(FONTS_DIR / "Roboto-Bold.ttf"))

        self.set_title(f"{invoice.invoice_number}")

        self.invoice_number = invoice.invoice_number
        self.tax_id = settings.tax_id
        self.iban = settings.iban
        self.bic = settings.bic
        self.additional_subheading = None
        if invoice.type == InvoiceType.KG:
            self.additional_subheading = "Physiotherapeutin"
        elif invoice.type == InvoiceType.GT:
            self.additional_subheading = "Gestalttherapeutin"

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
        self.set_font("Roboto", "B", 14)
        self.cell(0, new_x=XPos.LMARGIN, new_y=YPos.TMARGIN)
        self.ln(2.5)
        self.cell(25)
        self.cell(0, text="Mervi Fischbach", align="L")
        self.ln()
        self.cell(25)
        self.set_font("Roboto", "B", 12)
        self.set_text_color(150)
        self.cell(0, text="Heilpraktikerin", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(25)
        # hide Physiotherapy on HP Invoices
        if self.additional_subheading:
            self.cell(0, text=self.additional_subheading)
        self.ln(23)

    # Page footer
    def footer(self):
        """New PDF footer section"""

        # Position at 3.5 cm from bottom
        self.set_y(-35)
        self.set_font("Roboto", "B", INVOICE_FOOTER_FONT_SIZE)
        self.cell(0, 5, "Bankverbindung", align="C")
        self.ln(3)

        clean_iban = self.iban.replace(" ", "")
        formatted_iban = " ".join(clean_iban[i : i + 4] for i in range(0, len(clean_iban), 4))
        self.cell(0, 5, f"IBAN: {formatted_iban}", align="C")
        self.ln(3)
        self.cell(0, 5, f"BIC: {self.bic}", align="C")
        self.ln(3)
        self.set_font("Roboto", "", 6)
        self.cell(1, 5, f"Rechnungsnummer: {self.invoice_number}", align="L")

        clean_tax_id = self.tax_id.replace(" ", "").replace("/", "")
        parts = [clean_tax_id[:3], clean_tax_id[3:6], clean_tax_id[6:]]
        formatted_tax_id = "/".join(p for p in parts if p)
        self.cell(0, 5, f"Steuer Nummer: {formatted_tax_id} - Ust. Befreit nach §4 UStG", align="C")
        # Page number
        self.cell(0, 5, "Seite " + str(self.page_no()) + " von {nb}", align="R")
