from .document_pdf import DocumentPdf
from ..models import PatientDB, SettingsDB, Gender
from ..models.therapyClause_model import TherapyClauseDB
from ..utilities import RECIPIENT_OFFSET, NORMAL_FONT_SIZE, THERAPY_DEFAULT_OFFSET, THERAPY_FONT_SIZE, \
    THERAPY_HEADER_FONT_SIZE
from ..utilities.path_utilitiy import generate_therapy_path


class Therapy(DocumentPdf):
    """Creates the HP PDF and outputs to given filepath"""

    def __init__(
            self,
            patient: PatientDB,
            settings: SettingsDB,
            clauses: list[TherapyClauseDB],
    ):
        super().__init__("Therapie-Vereinbarung")

        self.set_title(f"{patient.patient_id}-{patient.label}-therapy")
        self.set_margins(17, 17, 17)

        # prepare data
        self.gender = "Mann" if patient.gender == Gender.MALE else "Frau"
        self.first_name = patient.first_name
        self.last_name = patient.last_name
        self.street = patient.street
        self.street_number = patient.street_number
        self.postal_code = patient.postal_code
        self.city = patient.city
        self.birthday = patient.birthday
        self.price_from = settings.price_from
        self.price_to = settings.price_to
        self.email = patient.email
        self.telephone = patient.telephone
        self.clauses = sorted(clauses, key=lambda c: c.number)

        self.filepath = generate_therapy_path(patient)

        self.create_pages()

    def create_pages(self):
        """Creates the PDF."""

        self.set_auto_page_break(True, 25)

        self.add_page()

        self.set_font("Roboto", size=7)
        self.cell(RECIPIENT_OFFSET)
        self.write(text="Mervi Fischbach - Schulgasse 9 - 86923 Finning")
        self.ln(3)

        self.set_font("Roboto", size=NORMAL_FONT_SIZE)
        self.cell(RECIPIENT_OFFSET)
        if self.gender == "Mann":
            self.write(text="Herr\n")
        elif self.gender == "Frau":
            self.write(text="Frau\n")
        self.cell(RECIPIENT_OFFSET)
        self.write(text=f"{self.first_name.strip()} {self.last_name}\n")
        self.cell(RECIPIENT_OFFSET)
        self.write(text=f"{self.street} {self.street_number}\n")
        self.cell(RECIPIENT_OFFSET)
        self.write(text=f"{self.postal_code} {self.city}\n")
        self.ln(27)

        self.set_font("Roboto", "B", 13)
        self.write(text="Therapie-Vereinbarung")
        self.ln(THERAPY_DEFAULT_OFFSET)

        self.set_font("Roboto", size=THERAPY_FONT_SIZE - 1)
        self.write(text="zwischen")
        self.ln(THERAPY_DEFAULT_OFFSET)

        self.set_font("Roboto", "B", THERAPY_HEADER_FONT_SIZE)
        self.write(text="Mervi Fischbach\n")
        self.set_font("Roboto", size=THERAPY_FONT_SIZE)
        self.write(text="Heilpraktikerin\n")
        self.write(text="Schulgasse 9 - 86923 Finning\n")
        self.write(text="Tel.: 08806 / 9587111\n")
        self.write(text="E-Mail: mervi.winter@web.de")
        self.ln(THERAPY_DEFAULT_OFFSET)

        self.set_font("Roboto", size=THERAPY_FONT_SIZE - 1)
        self.write(text="und Patient:")
        self.ln(THERAPY_DEFAULT_OFFSET)
        self.set_font("Roboto", "B", THERAPY_HEADER_FONT_SIZE)
        self.write(text=f"{self.first_name} {self.last_name}\n")
        self.set_font("Roboto", size=THERAPY_FONT_SIZE)
        self.write(text=f"{self.street} {self.street_number} - {self.postal_code} {self.city}\n")
        self.write(text=f"geb. {self.birthday}\n")
        if self.telephone != "":
            self.write(text=f"Tel.: {self.telephone}\n")
        if self.email != "":
            self.write(text=f"E-Mail: {self.email}")
        self.ln(8)
        self.cell(175, 0, border=1, center=True)
        self.ln(4)

        for clause in self.clauses:
            description = clause.description.format(
                price_from=self.price_from, price_to=self.price_to
            )

            with self.offset_rendering() as dummy:
                dummy.set_font("Roboto", "B", THERAPY_HEADER_FONT_SIZE)
                dummy.write(text=f"{clause.number}. {clause.title}\n")
                dummy.set_font("Roboto", size=THERAPY_FONT_SIZE)
                dummy.multi_cell(0, THERAPY_FONT_SIZE / 3, description)

            if dummy.page_break_triggered:
                self.add_page()

            self.set_font("Roboto", "B", THERAPY_HEADER_FONT_SIZE)
            self.write(text=f"{clause.number}. {clause.title}\n")
            self.set_font("Roboto", size=THERAPY_FONT_SIZE)
            self.multi_cell(0, THERAPY_FONT_SIZE / 3, description)
            self.ln(THERAPY_DEFAULT_OFFSET)

        self.ln(6)
        self.cell(175, 0, border=1, center=True)
        self.ln(2)

        self.set_font("Roboto", size=THERAPY_FONT_SIZE)
        self.multi_cell(
            0,
            THERAPY_FONT_SIZE / 3,
            "Ich willige hiermit nach ausreichender Bedenkzeit in die vorgeschlagene Behandlung ein. "
            "Eine Ausfertigung dieses Behandlungsvertrages habe ich erhalten",
        )

        self.set_draw_color(r=0, g=0, b=0)
        self.set_dash_pattern(dash=0.1, gap=1)
        self.line(x1=18.5, y1=262, x2=68.5, y2=262)
        self.line(x1=140, y1=262, x2=190, y2=262)
        self.set_y(264)
        self.set_x(17.5)
        self.set_font("Roboto", "", 7)
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
