from .document_pdf import DocumentPdf
from ..models import PatientDB, Gender
from ..models.privacyClause_model import PrivacyClauseDB
from ..utilities import DOCUMENT_IN_TEXT_OFFSET, DOCUMENT_DEFAULT_OFFSET, DOCUMENT_HEADER_FONT_SIZE, DOCUMENT_FONT_SIZE, \
    RECIPIENT_OFFSET
from ..utilities.path_utilitiy import generate_privacy_path


class Privacy(DocumentPdf):
    """Creates the Privacy PDF and outputs to generated filepath"""

    def __init__(self, patient: PatientDB, clauses: list[PrivacyClauseDB]):
        super().__init__("Datenschutzinformation und Einwilligungserklärung")

        self.set_title(f"{patient.patient_id}-{patient.label}-privacy")
        self.set_margins(17, 17, 17)

        self.gender = "Mann" if patient.gender == Gender.MALE else "Frau"
        self.first_name = patient.first_name
        self.last_name = patient.last_name
        self.street = patient.street
        self.street_number = patient.street_number
        self.postal_code = patient.postal_code
        self.city = patient.city
        self.birthday = patient.birthday
        self.email = patient.email or ""
        self.telephone = patient.telephone or ""
        self.clauses = sorted(clauses, key=lambda c: c.number)

        self.filepath = generate_privacy_path(patient)

        self.create_pages()

    def create_pages(self):
        """Creates the PDF."""

        self.set_auto_page_break(True, 25)

        self.add_page()

        self.set_font("helvetica", size=7)
        self.cell(RECIPIENT_OFFSET)
        self.write(text="Mervi Fischbach - Schulgasse 9 - 86923 Finning")
        self.ln(3)

        self.set_font("helvetica", size=DOCUMENT_FONT_SIZE)
        self.cell(RECIPIENT_OFFSET)
        if self.gender == "Mann":
            self.write(text="Herr\n")
        elif self.gender == "Frau":
            self.write(text="Frau\n")
        self.cell(RECIPIENT_OFFSET)
        self.write(text=f"{self.first_name} {self.last_name}\n")
        self.cell(RECIPIENT_OFFSET)
        self.write(text=f"{self.street} {self.street_number}\n")
        self.cell(RECIPIENT_OFFSET)
        self.write(text=f"{self.postal_code} {self.city}\n")
        self.ln(27)

        self.set_font("helvetica", "B", 13)
        self.write(text="Datenschutzinformation und Einwilligungserklärung")
        self.ln(DOCUMENT_DEFAULT_OFFSET)

        self.set_font("helvetica", size=DOCUMENT_FONT_SIZE - 1)
        self.write(text="zwischen")
        self.ln(DOCUMENT_DEFAULT_OFFSET)

        self.set_font("helvetica", "B", DOCUMENT_HEADER_FONT_SIZE)
        self.write(text="Mervi Fischbach\n")
        self.set_font("helvetica", size=DOCUMENT_FONT_SIZE)
        self.write(text="Heilpraktikerin\n")
        self.write(text="Schulgasse 9 - 86923 Finning\n")
        self.write(text="Tel.: 08806 / 9587111\n")
        self.write(text="E-Mail: mervi.winter@web.de")
        self.ln(DOCUMENT_DEFAULT_OFFSET)

        self.set_font("helvetica", size=DOCUMENT_FONT_SIZE - 1)
        self.write(text="und Patient:")
        self.ln(DOCUMENT_DEFAULT_OFFSET)
        self.set_font("helvetica", "B", DOCUMENT_HEADER_FONT_SIZE)
        self.write(text=f"{self.first_name} {self.last_name}\n")
        self.set_font("helvetica", size=DOCUMENT_FONT_SIZE)
        self.write(text=f"{self.street} {self.street_number} - {self.postal_code} {self.city}\n")
        self.write(text=f"geb. {self.birthday}\n")
        if self.telephone:
            self.write(text=f"Tel.: {self.telephone}\n")
        if self.email:
            self.write(text=f"E-Mail: {self.email}")
        self.ln(8)
        self.cell(175, 0, border=1, center=True)
        self.ln(4)

        for clause in self.clauses:
            paragraphs = clause.description.split("\n\n")

            with self.offset_rendering() as dummy:
                if not clause.is_preamble:
                    dummy.set_font("helvetica", "B", DOCUMENT_HEADER_FONT_SIZE)
                    dummy.write(text=f"{clause.number}. {clause.title}\n")
                dummy.set_font("helvetica", size=DOCUMENT_FONT_SIZE)
                for i, para in enumerate(paragraphs):
                    dummy.multi_cell(0, DOCUMENT_FONT_SIZE / 3, para)
                    if i < len(paragraphs) - 1:
                        dummy.ln(DOCUMENT_IN_TEXT_OFFSET)

            if dummy.page_break_triggered:
                self.add_page()

            if not clause.is_preamble:
                self.set_font("helvetica", "B", DOCUMENT_HEADER_FONT_SIZE)
                self.write(text=f"{clause.number}. {clause.title}\n")
            self.set_font("helvetica", size=DOCUMENT_FONT_SIZE)
            for i, para in enumerate(paragraphs):
                self.multi_cell(0, DOCUMENT_FONT_SIZE / 3, para)
                if i < len(paragraphs) - 1:
                    self.ln(DOCUMENT_IN_TEXT_OFFSET)
            self.ln(DOCUMENT_DEFAULT_OFFSET)

        self.set_draw_color(r=0, g=0, b=0)
        self.set_dash_pattern(dash=0.1, gap=1)
        self.line(x1=18.5, y1=262, x2=68.5, y2=262)
        self.line(x1=140, y1=262, x2=190, y2=262)
        self.set_y(264)
        self.set_x(17.5)
        self.set_font("helvetica", "", 7)
        self.multi_cell(0, 6 / 2.5, "Ort, Datum", align="L")
        self.set_y(264)
        self.set_x(139)
        self.multi_cell(
            0,
            6 / 2.5,
            "Unterschrift Klient:in\n(bei Minderjährigen zusätzlich auch der/die\nErziehungsberechtigte/gesetzlicher Vertreter)",
            align="L",
        )

        self.output(str(self.filepath))
