from ..models import Gender, InvoiceDB, SettingsDB
from ..utilities.config import CACHE_DIR, NORMAL_FONT_SIZE, RECIPIENT_OFFSET, TREATMENT_FONT_SIZE
from .invoice_pdf import InvoicePdf


class InvoiceKgGt(InvoicePdf):
    """Creates the KG PDF and outputs to given filepath"""

    def __init__(self, invoice: InvoiceDB, settings: SettingsDB):
        super().__init__(invoice, settings)

        self.set_margins(17, 17, 17)

        # Patientdata
        self.label = invoice.patient.label
        self.gender = "Frau" if invoice.patient.gender == Gender.FEMALE else "Mann"
        self.first_name = invoice.patient.first_name
        self.last_name = invoice.patient.last_name
        self.street = invoice.patient.street
        self.street_number = invoice.patient.street_number
        self.city = invoice.patient.city
        self.postal_code = invoice.patient.postal_code
        self.birthday = invoice.patient.birthday.strftime("%d.%m.%Y") if invoice.patient.birthday else ""

        # Invoicedata
        self.filepath = CACHE_DIR / f"{invoice.invoice_number}.pdf"

        self.date_count = len(invoice.dates)
        self.total = f"{invoice.total:.2f}".replace(".", ",")

        ## DETAILS TABLE (TABLE 1)
        self.details_table = [
            ["Patientenkürzel", "Rechnungsnummer", "Rechnungsdatum"],
            [self.label, invoice.invoice_number, invoice.invoice_date.strftime("%d.%m.%Y")],
        ]

        ## DATES TABLE (TABLE 2)
        self.dates_table = []
        all_dates = [d.date.strftime("%d.%m.%Y") for d in sorted(invoice.dates, key=lambda x: x.date)]
        self.dates_table = [all_dates[i : i + 2] for i in range(0, len(all_dates), 2)]
        # here I might need to add a padding element if last row has only 1 element

        ## TREATMENT TABLE (TABLE 3)
        self.treatment_table = [["Anzahl", "Art der Behandlung", "Einzelpreis", "Gesamtpreis", ""]]
        # removed Anamnese but this should be in the items anyway
        self.treatment_table += [
            [
                str(item.quantity if item.quantity is not None else len(all_dates)),
                item.description,
                f"{item.amount:.2f}".replace(".", ","),
                f"{(item.amount * (item.quantity if item.quantity is not None else len(all_dates))):.2f}".replace(
                    ".", ","
                ),
                "€",  # Das Symbol-Feld am Ende
            ]
            for item in invoice.items
        ]

        ## TOTAL TABLE (TABLE 4)
        self.total_table = [["", "Gesamtbetrag:", self.total, "€"], ["", "", "", ""]]

        self.create_pages()

    def create_pages(self):
        """Creates the PDF. Checks also checks for linebreak so content is not
        split between 2 pages"""

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
        self.write(text=f"{self.first_name} {self.last_name}\n")
        self.cell(RECIPIENT_OFFSET)
        self.write(text=f"{self.street} {self.street_number}\n")
        self.cell(RECIPIENT_OFFSET)
        self.write(text=f"{self.postal_code} {self.city}\n")
        self.ln(24)

        self.cell(175, 0, border=1, center=True)
        self.set_font("Roboto", size=NORMAL_FONT_SIZE)
        with self.table(
            borders_layout="NONE",
            line_height=int(1.5 * self.font_size),
            text_align=("LEFT", "CENTER", "RIGHT"),
        ) as table:
            for data_row in self.details_table:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)
        self.cell(175, 0, border=1, center=True)
        self.ln(5)

        self.set_font("Roboto", style="B", size=NORMAL_FONT_SIZE)
        if self.gender == "Mann":
            self.cell(25, text="Patient:", align="L")
        elif self.gender == "Frau":
            self.cell(25, text="Patientin:", align="L")
        self.set_font("Roboto", style="", size=NORMAL_FONT_SIZE)
        self.cell(40, text=f"{self.first_name} {self.last_name}, geb. {self.birthday}")
        self.ln(7)

        self.set_font("Roboto", style="B", size=NORMAL_FONT_SIZE)
        self.write(text=f"{self.date_count} Behandlungstermine:")
        self.set_font("Roboto", style="", size=NORMAL_FONT_SIZE)
        self.ln(5)
        with self.table(
            width=80,
            line_height=int(1.7 * self.font_size),
            align="LEFT",
            borders_layout="NONE",
            first_row_as_headings=False,
        ) as table:
            for data_row in self.dates_table:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)
        self.ln(10)

        self.set_font("Roboto", size=NORMAL_FONT_SIZE)
        if self.gender == "Mann":
            self.write(
                text=f"Sehr geehrter Herr {self.last_name},\n\n"
                f"hiermit erlaube ich mir, für meine Bemühungen folgendes "
                f"Honorar zu berechnen:"
            )
        if self.gender == "Frau":
            self.write(
                text=f"Sehr geehrte Frau {self.last_name},\n\n"
                f"hiermit erlaube ich mir, für meine Bemühungen folgendes "
                f"Honorar zu berechnen:"
            )
        self.ln(7)
        self.set_font("Roboto", size=TREATMENT_FONT_SIZE)

        with self.table(
            cell_fill_color=230,
            cell_fill_mode="ROWS",
            line_height=int(1.7 * self.font_size),
            text_align=("CENTER", "LEFT", "RIGHT", "RIGHT", "LEFT"),
            col_widths=(9, 69, 13, 15, 4),
        ) as table:
            for data_row in self.treatment_table:
                row = table.row()
                for index, datum in enumerate(data_row):
                    row.cell(datum)

        self.ln(1)
        self.cell(175, 0, border=1, center=True)
        with self.table(
            borders_layout="NONE",
            col_widths=(9, 69, 13, 15, 4),
            line_height=int(1.7 * self.font_size),
            text_align=("CENTER", "RIGHT", "RIGHT", "RIGHT", "LEFT"),
            cell_fill_color=180,
            cell_fill_mode="NONE",
            first_row_as_headings=False,
        ) as table:
            for data_row in self.total_table:
                row = table.row()
                for index_2, datum in enumerate(data_row):
                    if index_2 == 1:
                        self.set_font("Roboto", style="B", size=TREATMENT_FONT_SIZE)
                        row.cell(datum, colspan=2)
                        self.set_font("Roboto", style="", size=TREATMENT_FONT_SIZE)
                    elif index_2 == 3:
                        self.set_font("Roboto", style="", size=TREATMENT_FONT_SIZE)
                        row.cell(datum)
                    else:
                        self.set_font("Roboto", style="B", size=TREATMENT_FONT_SIZE)
                        row.cell(datum)
                        self.set_font("Roboto", style="", size=TREATMENT_FONT_SIZE)

        self.ln(0)
        self.set_font("Roboto", size=NORMAL_FONT_SIZE)
        self.write(
            6.5,
            text=f"Ich bitte Sie, den Gesamtbetrag von {self.total} € "
            f"innerhalb von 14 Tagen unter Angabe der Rechnungsnummer auf "
            f"unten stehendes Konto zu überweisen.",
        )
        self.ln(13)
        self.write(text="Mit freundlichen Grüßen")
        self.ln(7)
        self.write(text="Mervi Fischbach")

        self.output(str(self.filepath))
