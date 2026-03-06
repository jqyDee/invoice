from fpdf import FPDF, XPos, YPos

from app.utilities import LOGO_PATH, FONTS_DIR


class DocumentPdf(FPDF):
    """overwrites the default FPDF2 header and footer functions for HP Rechnung."""

    def __init__(self, footer_note: str):
        super().__init__()

        self.add_font(
            family="Roboto",
            style="",
            fname=str(FONTS_DIR / "Roboto-Regular.ttf")
        )

        self.add_font(
            family="Roboto",
            style="B",
            fname=str(FONTS_DIR / "Roboto-Bold.ttf")
        )

        self.footer_note = footer_note

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
        self.cell(0, text="Heilpraktikerin", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(25)
        self.set_text_color(255)
        self.cell(0, text="Physiotherapeutin")
        self.ln(23)

    # Page footer
    def footer(self):
        """New PDF footer section"""

        # Position at 3.5 cm from bottom
        self.set_y(-25)

        # Page number
        self.set_font("helvetica", "", 6)
        self.cell(1, 5, f"{self.footer_note} | Stand 2018", align="L")
        self.cell(0, 5, "Seite " + str(self.page_no()) + " von {nb}", align="R")

