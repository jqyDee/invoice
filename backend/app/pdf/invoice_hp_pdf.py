from ..models import InvoiceDB, SettingsDB, Gender
from ..pdf.invoice_pdf import InvoicePdf
from ..utilities.config import NORMAL_FONT_SIZE, TREATMENT_FONT_SIZE, RECIPIENT_OFFSET, CACHE_DIR
from ..schemas import InvoiceItem


class InvoiceHp(InvoicePdf):
    """Creates the HP PDF and outputs to given filepath"""


    def __init__(
            self,
            invoice: InvoiceDB,
            settings: SettingsDB,
    ):
        super().__init__(invoice, settings, hide_physio=True)

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

        sorted_items: list[InvoiceItem] = sorted(invoice.items, key=lambda x: x.date)
        for i in sorted_items:
            word_count = len(i.description.split())
            col_5_content = "\u00a0\n" * word_count

            amount_str = f"{i.amount:.2f}".replace(".", ",")

            self.treatment_table.append([i.date.strftime("%d.%m.%y"), str(i.number), i.description, amount_str, col_5_content])

        ## TOTAL TABLE (TABLE 4)
        self.total_table = [
            ["", "", "Gesamtbetrag:", self.total, "\u00a0"],
            ["", "", "", "", ""]
        ]

        self.create_pages()


    def create_pages(self):
        """Creates the PDF. Checks also checks for linebreak so content is not
        split between 2 pages"""

        self.set_auto_page_break(True, 35)

        self.add_page()

        self.set_font("helvetica", size=7)
        self.cell(RECIPIENT_OFFSET)
        self.write(text="Mervi Fischbach - Schulgasse 9 - 86923 Finning")
        self.ln(3)

        self.set_font("helvetica", size=NORMAL_FONT_SIZE)
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
        self.set_font("helvetica", size=NORMAL_FONT_SIZE)

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

        self.set_font("helvetica", style="B", size=NORMAL_FONT_SIZE)
        if self.gender == "Mann":
            self.cell(25, text="Patient:", align="L")
        elif self.gender == "Frau":
            self.cell(25, text="Patientin:", align="L")
        self.set_font("helvetica", style="", size=NORMAL_FONT_SIZE)
        self.cell(40, text=f"{self.first_name} {self.last_name}, geb. {self.birthday}")

        self.ln(7)
        self.set_font("helvetica", style="B", size=NORMAL_FONT_SIZE)
        self.cell(25, text="Diagnose:", align="L")
        self.set_font("helvetica", style="", size=NORMAL_FONT_SIZE)
        self.multi_cell(135, text=f"{self.diagnosis}")

        # offset rendering the main table and the total
        # making sure it is not split in half
        with self.offset_rendering() as dummy:
            dummy.cell(175, 0, border=1, center=True)
            dummy.ln(10)
            if self.gender == "Mann":
                dummy.write(
                    text=f"Sehr geehrter Herr {self.last_name},\n\n"
                         f"hiermit erlaube ich mir, für meine Bemühungen folgendes "
                         f"Honorar zu berechnen:"
                )
            if self.gender == "Frau":
                dummy.write(
                    text=f"Sehr geehrte Frau {self.last_name},\n\n"
                         f"hiermit erlaube ich mir, für meine Bemühungen "
                         f"folgendes Honorar zu berechnen:"
                )
            dummy.ln(7)
            dummy.set_font("helvetica", size=TREATMENT_FONT_SIZE)

            # Table 2
            # -----------------
            # Date | Ziffern | Descriptions | Costs
            with dummy.table(
                    cell_fill_color=230,
                    cell_fill_mode="ROWS",
                    line_height=int(1.7 * self.font_size),
                    text_align=("CENTER", "RIGHT", "LEFT", "RIGHT", "LEFT"),
                    col_widths=(10, 8, 70, 10, 4),
            ) as table:
                for index1, data_row in enumerate(self.treatment_table):
                    row = table.row()
                    for index2, datum in enumerate(data_row):
                        if index2 == 4:
                            dummy.set_font("symbol", size=TREATMENT_FONT_SIZE + 1)
                            row.cell(datum)
                            dummy.set_font(
                                "helvetica", style="", size=TREATMENT_FONT_SIZE
                            )
                        else:
                            row.cell(datum)

            dummy.ln(1)
            dummy.cell(175, 0, border=1, center=True)

            # Table 3
            # --------------
            #      |      | Gesamtbetrag | Total
            with dummy.table(
                    borders_layout="NONE",
                    col_widths=(10, 8, 70, 10, 4),
                    line_height=int(1.7 * self.font_size),
                    text_align=("CENTER", "LEFT", "RIGHT", "RIGHT", "LEFT"),
                    cell_fill_color=180,
                    cell_fill_mode="NONE",
                    first_row_as_headings=False,
            ) as table:
                page_before = dummy.page_no()
                for data_row in self.total_table:
                    row = table.row()
                    for index, datum in enumerate(data_row):
                        if index == 4:
                            dummy.set_font("symbol", "", size=TREATMENT_FONT_SIZE + 1)
                            row.cell(datum)
                            dummy.set_font(
                                "helvetica", style="", size=TREATMENT_FONT_SIZE
                            )
                        else:
                            dummy.set_font(
                                "helvetica", style="B", size=TREATMENT_FONT_SIZE
                            )
                            row.cell(datum)
                            dummy.set_font(
                                "helvetica", style="", size=TREATMENT_FONT_SIZE
                            )

            man_page_break = False
            if page_before != dummy.page_no():
                man_page_break = True

        if man_page_break:
            self.table_data_2_1 = list(self.treatment_table)
            while len(self.table_data_2_1) > 2:
                self.table_data_2_1.pop(1)
            self.treatment_table.pop(-1)

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
        self.set_font("helvetica", size=TREATMENT_FONT_SIZE)

        # Table 2
        # -----------------
        # Date | Ziffern | Descriptions | Costs
        with self.table(
                cell_fill_color=230,
                cell_fill_mode="ROWS",
                line_height=int(1.7 * self.font_size),
                text_align=("CENTER", "RIGHT", "LEFT", "RIGHT", "LEFT"),
                col_widths=(10, 8, 70, 10, 4),
        ) as table:
            for data_row in self.treatment_table:
                row = table.row()
                for index, datum in enumerate(data_row):
                    if index == 4:
                        self.set_font("symbol", size=TREATMENT_FONT_SIZE + 1)
                        row.cell(datum)
                        self.set_font(
                            "helvetica", style="", size=TREATMENT_FONT_SIZE
                        )
                    else:
                        row.cell(datum)

        # only when table 2 and 3 are separated
        # Table 2.1
        # -----------------
        # Date | Ziffern | Descriptions | Costs
        if self.table_data_2_1:
            self.add_page()
            with self.table(
                    cell_fill_color=230,
                    cell_fill_mode="ROWS",
                    line_height=int(1.7 * self.font_size),
                    text_align=("CENTER", "RIGHT", "LEFT", "RIGHT", "LEFT"),
                    col_widths=(10, 8, 70, 10, 4),
            ) as table:
                for data_row in self.table_data_2_plus:
                    row = table.row()
                    for index, datum in enumerate(data_row):
                        if index == 4:
                            self.set_font("symbol", size=TREATMENT_FONT_SIZE + 1)
                            row.cell(datum)
                            self.set_font(
                                "helvetica", style="", size=TREATMENT_FONT_SIZE
                            )
                        else:
                            row.cell(datum)

        self.ln(1)
        self.cell(175, 0, border=1, center=True)

        # Table 3
        # --------------
        #      |      | Gesamtbetrag | Total
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
                for index, datum in enumerate(data_row):
                    if index == 4:
                        self.set_font("symbol", "", size=TREATMENT_FONT_SIZE + 1)
                        row.cell(datum)
                        self.set_font(
                            "helvetica", style="", size=TREATMENT_FONT_SIZE
                        )
                    else:
                        self.set_font(
                            "helvetica", style="B", size=TREATMENT_FONT_SIZE
                        )
                        row.cell(datum)
                        self.set_font(
                            "helvetica", style="", size=TREATMENT_FONT_SIZE
                        )

        self.ln(3)

        with self.offset_rendering() as dummy:
            dummy.write(
                6.5, text=f"Ich bitte Sie, den Gesamtbetrag von {self.total} "
            )
            dummy.set_font("symbol", size=NORMAL_FONT_SIZE + 1)
            dummy.write(6.5, text="\u00a0 ")
            dummy.set_font("helvetica", size=NORMAL_FONT_SIZE)
            dummy.write(
                6.5,
                text="innerhalb von 14 Tagen unter Angabe der Rechnungsnummer auf unten "
                     "stehendes Konto zu überweisen.",
            )
            dummy.ln(13)
            dummy.write(text="Mit freundlichen Grüßen")
            dummy.ln(10)
            dummy.write(text="Mervi Fischbach")

        if dummy.page_break_triggered:
            self.add_page()

        self.set_font("helvetica", size=NORMAL_FONT_SIZE)
        self.write(6.5, text=f"Ich bitte Sie, den Gesamtbetrag von {self.total} ")
        self.set_font("symbol", size=NORMAL_FONT_SIZE + 1)
        self.write(6.5, text="\u00a0 ")
        self.set_font("helvetica", size=NORMAL_FONT_SIZE)
        self.write(
            6.5,
            text="innerhalb von 14 Tagen unter Angabe der Rechnungsnummer auf unten "
                 "stehendes Konto zu überweisen.",
        )
        self.ln(13)
        self.write(text="Mit freundlichen Grüßen")
        self.ln(7)
        self.write(text="Mervi Fischbach")

        self.output(str(self.filepath))
