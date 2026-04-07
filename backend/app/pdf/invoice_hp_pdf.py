from ..models import InvoiceDB, SettingsDB, Gender
from ..pdf.invoice_pdf import InvoicePdf
from ..utilities.config import NORMAL_FONT_SIZE, TREATMENT_FONT_SIZE, RECIPIENT_OFFSET
from ..utilities.path_utilitiy import generate_invoice_path


class InvoiceHp(InvoicePdf):
    """Creates the HP PDF and outputs to given filepath"""

    def __init__(
            self,
            invoice: InvoiceDB,
            settings: SettingsDB,
    ):
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
        self.filepath = generate_invoice_path(invoice)

        self.diagnosis = invoice.diagnosis
        self.total = f"{invoice.total:.2f}".replace(".", ",")

        ## DETAILS TABLE (TABLE 1)
        self.details_table = [
            ["Patientenkürzel", "Rechnungsnummer", "Rechnungsdatum"],
            [self.label, invoice.invoice_number, invoice.invoice_date.strftime("%d.%m.%Y")]
        ]

        ## TREATMENT TABLE (TABLE 2)
        ### ????
        self.table_data_2_1 = None

        self.treatment_table = [["Datum", "Ziffer", "Art der Behandlung", "Betrag", ""]]
        self.manual_pagebreak = False

        for d in sorted(invoice.dates, key=lambda date: date.date):
            date_str = d.date.strftime("%d.%m.%y") + "\n"
            date_str += "\n".join("" for _ in d.items)

            ziffern_str = "\n".join(str(i.number) for i in d.items)
            desc_str = "\n".join(i.description for i in d.items)
            amount_str = "\n".join(f"{i.amount:.2f}".replace(".", ",") for i in d.items)

            euro_str = "\n".join("€" for _ in d.items)

            self.treatment_table.append([
                date_str,
                ziffern_str,
                desc_str,
                amount_str,
                euro_str
            ])

        ## TOTAL TABLE (TABLE 4)
        self.total_table = [
            ["", "", "Gesamtbetrag:", self.total, "€"],
            ["", "", "", "", ""]
        ]

        self.create_pages()

    def create_pages(self):
        """Creates the PDF. Checks also checks for linebreak so content is not
        split between 2 pages"""

        self.set_auto_page_break(True, 35)

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
        self.ln(27)

        self.cell(175, 0, border=1, center=True)
        self.set_font("Roboto", size=NORMAL_FONT_SIZE)

        # Table 1
        # ----------------------
        # Kuerzel | ReNr | Date
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
        self.cell(25, text="Diagnose:", align="L")
        self.set_font("Roboto", style="", size=NORMAL_FONT_SIZE)
        self.multi_cell(135, text=f"{self.diagnosis}")

        self.cell(175, 0, border=1, center=True)
        self.ln(10)
        if self.gender == "Mann":
            self.write(
                text=f"Sehr geehrter Herr {self.last_name},\n\n"
                     f"hiermit erlaube ich mir, für meine Bemühungen folgendes "
                     f"Honorar zu berechnen:"
            )
        if self.gender == "Frau":
            self.write(
                text=f"Sehr geehrte Frau {self.last_name},\n\n"
                     f"hiermit erlaube ich mir, für meine Bemühungen "
                     f"folgendes Honorar zu berechnen:"
            )
        self.ln(7)
        self.set_font("Roboto", size=TREATMENT_FONT_SIZE)

        # TABLE SETUP
        headers = self.treatment_table[0]
        treatments = self.treatment_table[1:]

        main_treatments = treatments[:-1] if len(treatments) > 1 else treatments
        last_treatment = treatments[-1:] if len(treatments) > 1 else None

        last_treatment_row_color = 255 if len(treatments) % 2 == 0 else 230

        if main_treatments:
            with self.table(
                    cell_fill_color=230,
                    cell_fill_mode="ROWS",
                    line_height=int(1.7 * self.font_size),
                    text_align=("CENTER", "RIGHT", "LEFT", "RIGHT", "LEFT"),
                    col_widths=(10, 8, 70, 10, 4),
                    first_row_as_headings=True
            ) as table:
                row = table.row()
                for datum in headers:
                    row.cell(datum)

                for data_row in main_treatments:
                    row = table.row()
                    for index, datum in enumerate(data_row):
                        row.cell(datum)

        # ============== DUMMY ==============
        with self.offset_rendering() as dummy:
            if last_treatment:
                with dummy.table(
                        cell_fill_color=230,
                        cell_fill_mode="ROWS",
                        line_height=int(1.7 * self.font_size),
                        text_align=("CENTER", "RIGHT", "LEFT", "RIGHT", "LEFT"),
                        col_widths=(10, 8, 70, 10, 4),
                        first_row_as_headings=False
                ) as table:
                    row = table.row()
                    for datum in last_treatment[0]:
                        row.cell(datum)

            dummy.ln(1)
            dummy.cell(175, 0, border=1, center=True)

            with dummy.table(
                    borders_layout="NONE",
                    col_widths=(10, 8, 70, 10, 4),
                    line_height=int(1.7 * self.font_size),
                    text_align=("CENTER", "LEFT", "RIGHT", "RIGHT", "LEFT"),
                    cell_fill_color=180,
                    cell_fill_mode="NONE",
                    first_row_as_headings=False,
            ) as table:
                for data_row in self.total_table:
                    row = table.row()
                    for datum in data_row:
                        if datum != '€':
                            self.set_font("Roboto", style="B", size=TREATMENT_FONT_SIZE)
                        row.cell(datum)
                        self.set_font("Roboto", style="", size=TREATMENT_FONT_SIZE)

        if dummy.page_break_triggered:
            self.add_page()
        # ============== DUMMY ==============

        if last_treatment:
            with self.table(
                cell_fill_color=last_treatment_row_color,
                cell_fill_mode="ALL",
                line_height=int(1.7 * self.font_size),
                text_align=("CENTER", "RIGHT", "LEFT", "RIGHT", "LEFT"),
                col_widths=(10, 8, 70, 10, 4),
                first_row_as_headings=False,  # No headers for the appended row
            ) as table:
                row = table.row()
                for datum in last_treatment[0]:
                    row.cell(datum)

        self.ln(1)
        self.cell(175, 0, border=1, center=True)

        with self.table(
                borders_layout="NONE",
                col_widths=(10, 8, 70, 10, 4),
                line_height=int(1.7 * self.font_size),
                text_align=("CENTER", "LEFT", "RIGHT", "RIGHT", "LEFT"),
                cell_fill_color=180,
                cell_fill_mode="NONE",
                first_row_as_headings=False,
        ) as table:
            for data_row in self.total_table:
                row = table.row()
                for datum in data_row:
                    if datum != '€':
                        self.set_font("Roboto", style="B", size=TREATMENT_FONT_SIZE)
                    row.cell(datum)
                    self.set_font("Roboto", style="", size=TREATMENT_FONT_SIZE)

        with self.offset_rendering() as dummy:
            dummy.write(
                6.5, text=f"Ich bitte Sie, den Gesamtbetrag von {self.total} € "
                          f"innerhalb von 14 Tagen unter Angabe der Rechnungsnummer auf unten "
                          f"stehendes Konto zu überweisen.",
            )
            dummy.ln(13)
            dummy.write(text="Mit freundlichen Grüßen")
            dummy.ln(10)
            dummy.write(text="Mervi Fischbach")

        if dummy.page_break_triggered:
            self.add_page()

        self.set_font("Roboto", size=NORMAL_FONT_SIZE)
        self.write(
            6.5,
            text=f"Ich bitte Sie, den Gesamtbetrag von {self.total} € "
                 f"innerhalb von 14 Tagen unter Angabe der Rechnungsnummer auf unten "
                 f"stehendes Konto zu überweisen.",
        )
        self.ln(13)
        self.write(text="Mit freundlichen Grüßen")
        self.ln(7)
        self.write(text="Mervi Fischbach")

        self.output(str(self.filepath))
