from .document_pdf import DocumentPdf


class Therapy(DocumentPdf):
    """Creates the HP PDF and outputs to given filepath"""

    # setting pdf font sizes
    header_font_size = 10
    normal_font_size = 8
    privacy_font_size = 7

    rechnungsempfaenger_offset = 4
    default_offset = 6
    in_text_offset = 3

    def __init__(self, stammdaten: list, filepath: str, price_from: str, price_to: str):
        super().__init__("Therapie-Vereinbarung")

        self.set_margins(17, 17, 17)

        # prepare data
        self.kuerzel = stammdaten[0]
        self.mann_frau = stammdaten[1]
        self.nachname = stammdaten[2]
        self.vorname = stammdaten[3]
        self.strasse = stammdaten[4]
        self.hausnummer = stammdaten[5]
        self.plz = stammdaten[6]
        self.ort = stammdaten[7]
        self.geburtsdatum = stammdaten[8]
        self.price_from = price_from
        self.price_to = price_to
        try:
            self.email = stammdaten[11]
        except IndexError:
            self.email = ""
        try:
            self.telefon = stammdaten[13]
        except IndexError:
            self.telefon = ""

        self.create_pages(filepath)

    def create_pages(self, filepath):
        """Creates the PDF."""

        self.set_auto_page_break(True, 25)

        self.add_page()

        self.set_font("helvetica", size=7)
        self.cell(self.rechnungsempfaenger_offset)
        self.write(text="Mervi Fischbach - Schulgasse 9 - 86923 Finning")
        self.ln(3)

        self.set_font("helvetica", size=self.normal_font_size)
        self.cell(self.rechnungsempfaenger_offset)
        if self.mann_frau == "Mann":
            self.write(text="Herr\n")
        elif self.mann_frau == "Frau":
            self.write(text="Frau\n")
        self.cell(self.rechnungsempfaenger_offset)
        self.write(text=f"{self.vorname} {self.nachname}\n")
        self.cell(self.rechnungsempfaenger_offset)
        self.write(text=f"{self.strasse} {self.hausnummer}\n")
        self.cell(self.rechnungsempfaenger_offset)
        self.write(text=f"{self.plz} {self.ort}\n")
        self.ln(27)

        self.set_font("helvetica", "B", 13)
        self.write(text="Therapie-Vereinbarung")
        self.ln(self.default_offset)

        self.set_font("helvetica", size=self.normal_font_size - 1)
        self.write(text="zwischen")
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="Mervi Fischbach\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.write(text="Heilpraktikerin\n")
        self.write(text="Schulgasse 9 - 86923 Finning\n")
        self.write(text="Tel.: 08806 / 9587111\n")
        self.write(text="E-Mail: mervi.winter@web.de")
        self.ln(self.default_offset)

        self.set_font("helvetica", size=self.normal_font_size - 1)
        self.write(text="und Patient:")
        self.ln(self.default_offset)
        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text=f"{self.vorname} {self.nachname}\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.write(text=f"{self.strasse} {self.hausnummer} - {self.plz} {self.ort}\n")
        self.write(text=f"geb. {self.geburtsdatum}\n")
        if self.telefon != "":
            self.write(text=f"Tel.: {self.telefon}\n")
        if self.email != "":
            self.write(text=f"E-Mail: {self.email}")
        self.ln(8)
        self.cell(175, 0, border=1, center=True)
        self.ln(4)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="1. VERTRAGSGEGENSTAND\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Vertragsgegenstand ist eine physiotherapeutische / heilkundliche Behandlung des "
            "Patienten. Die Behandlungen der Heilpraktikerin umfassen unter anderem "
            "auch wissenschaftlich / schulmedizinisch nicht anerkannte naturheilkundliche Heilverfahren.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="2. VERSPRECHEN AUF HEILUNG\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Auf alle Behandlungsmethoden wird keine Garantie auf Heilung oder Linderung gegeben. "
            "Es wird ausdrücklich darauf hingewiesen, dass kein Versprechen auf Heilung gemäß "
            "Heilmittelwerbegesetz (HWG) gegeben wird.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="3. BEHANDLUNGSHINWEIS\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Der Patient wird darauf hingewiesen, dass die Behandlung eine ärztliche Therapie nicht "
            "vollständig ersetzt. Sofern ärztlicher Rat erforderlich ist, wird die Therapeutin "
            "unverzüglich eine Weiterleitung an einen Arzt veranlassen. Dies gilt auch dann, wenn der "
            "Therapeutin aufgrund eines gesetzlichen Tätigkeitsverbots eine Behandlung nicht möglich ist.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="4. SCHWEIGEPFLICHT\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Die Therapeutin verpflichtet sich, über alles Wissen, das sie in ihrer Berufsausübung "
            "über die Patienten erhält, Stillschweigen zu bewahren. Sie offenbart das Berufsgeheimnis nur "
            "dann, wenn der Patient sie von der Schweigepflicht entbindet bzw. entbunden hat. Ausnahme: "
            "Die Therapeutin ist  jedoch von der Schweigepflicht befreit, wenn sie aufgrund gesetzlicher "
            "Vorschriften zur Weitergabe von Daten verpflichtet ist - beispielsweise Meldepflicht bei "
            "bestimmten Diagnosen - oder auf behördliche oder gerichtliche Anordnung auskunftspflichtig "
            "ist / wird. Dies gilt für: NAME VORNAME, STRASSE, PLZ ORT, GEBURTSDATUM, TELEFON, DIAGNOSE, "
            "KRANKENKASSE/VERSICHERUNG auch bei Auskünften an Personensorgeberechtigte, nicht aber für "
            "Auskünfte an Ehegatten, Verwandte oder Familienangehörige.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="5. SORGFALTSPFLICHT\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Die Therapeutin betreut ihre Patienten mit der größtmöglichen Sorgfalt. Sie wendet jene "
            "Heilmethoden an, die nach ihrer Überzeugung und ihrem Ausbildungsstand auf dem einfachsten, "
            "schnellsten und kostengünstigsten Weg zur Linderung und ggf. zur Heilung (kein "
            "Heilversprechen) der Beschwerden führen können.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="6. AUFKLÄRUNGSPFLICHT / AUFKLÄRUNGSUMFANGT\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Die Therapeutin ist verpflichtet, dem Patienten in verständlicher Weise zu Beginn der "
            "Behandlung und, soweit erforderlich, in deren Verlauf sämtliche für die Behandlung "
            "wesentlichen Umstände zu erläutern, insbesondere die Diagnose und die Therapie, sowie die "
            "voraussichtliche gesundheitliche Entwicklung. Mit seiner Unterschrift unter diesen Vertrag "
            "bestätigt der Patient, dass nachfolgende Punkte umfassend besprochen wurden: sein "
            "Gesundheitszustand, die Art der Erkrankung, die Behandlungsmethode und deren "
            "voraussichtliche Dauer, die zur Verfügung stehenden Behandlungsalternativen, Belastungen, "
            "Risiken und Erfolgschancen der Therapie.",
        )
        self.ln(self.default_offset)

        self.add_page()
        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="7. ERSTATTUNG DER BEHANDLUNGSKOSTEN DURCH DIE KRANKENKASSEN\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Die gesetzliche Krankenkassen und Ersatzkassen erstatten die Behandlungskosten für "
            "Heilpraktiker in der Regel nicht. Bei Privatkassen bzw. privaten Zusatzversicherung erfolgt "
            "die Erstattung von Behandlungskosten nur im Rahmen Ihres Versicherungsvertrages und meist "
            "nicht alle Heilkundeverfahren. Auch wird die volle Rechnungshöhe i.d.R. nicht erstattet. Es "
            "obliegt dem Patienten sich bei seiner Krankenversicherung zu erkundigen. Der Honoraranspruch "
            "der Heilpraktikerin gegenüber dem Patienten besteht unabhängig von "
            "jeglicher Krankenversicherungsleistung und/oder Beihilfeleistung in voller Höhe.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="8. HONORARVEREINBARUNG / BEHANDLUNGSKOSTEN\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.write(
            text="Das Honorar wird nach realem Zeitaufwand berechnet.\nDas Honorar für die Behandlungen beträgt:\n"
        )
        self.write(
            text=f"\t\t-\t\tMontag - Freitag: Euro {self.price_from}.00 - {self.price_to}.00 / Std (ca. 60 Minuten)\n"
        )
        self.write(text=f"\t\t-\t\tWochenende: Euro 130.00 (ca. 60 Minuten)\n")
        self.write(text=f"\t\t-\t\tErstanamnese: Euro 150.00 (ca. 90 Minuten)\n")
        self.write(
            text=f"\t\t-\t\tTelefonische Beratung:Montag - Freitag Euro 25.00 (ca 15 Minuten)\n"
        )
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Die Rechnungsausstellung erfolgt auf Grundlage der Gebührenordnung für Therapeuten (GebüTh) "
            "oder der Gebührenordnung für Heilpraktiker (GebüH). ",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="9. BERATUNG / NACHBETREUUNG ÜBER TELEFON\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Die Beratung / Nachbetreuung per Telefon ersetzt die reguläre Behandlung in der Praxis "
            "nicht und wird zusätzlich zu den persönlichen Terminen angeboten. Über Telefon können keine "
            "Diagnosen gestellt werden, dies geschieht nur in der Praxis. Die telefonische Beratung wird "
            "Montag - Freitag mit Euro 25  (¼ Std.) berechnet. ",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="10. LABORKOSTEN / KOSTEN FÜR MEDIKAMENTE\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Die Kosten für Laboruntersuchungen von Fremdlaboren gehen zu Lasten und auf Rechnung "
            "des Patienten. Alle Medikamente gehören zu den Eigenleistungen des Patienten. Ich möchte "
            "darauf hinweisen, dass Heilpraktiker keine verschreibungspflichtigen Medikamente verordnen "
            "dürfen.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(
            text="11. ENTSCHÄDIGUNG BEI NICHT- BZW. KURZFRISTIGER TERMINABSAGE\n"
        )
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Falls vereinbarte Therapietermine nicht wahrgenommen werden können, bitte ich Sie, "
            "diese spätestens 48 Stunden vorher abzusagen. Ich bitte weiterhin um Verständnis, dass ich bei"
            " Nicht- oder kurzfristiger Absage ein Ausfallhonorar in voller Höhe (100%) der normalen "
            "Therapiestunde berechne, da Ihr Termin leider so kurzfristig nicht belegt werden kann.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="12. RECHNUNGSZAHLUNG\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Der Zahlungsspielraum für gestellte Rechnungen liegt bei 14 Tagen ab Rechnungsdatum. "
            "Bitte haben Sie Verständnis, daß nach diesem Zeitraum zusätzlich Mahngebühren in Rechnung "
            "gestellt werden.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="13. PERSÖNLICHE PATIENTENDATEN UND MEDIZINISCHE BEFUNDE\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Es wird darauf hingewiesen, dass alle persönlichen und behandlungsrelevanten Angaben "
            "sowie medizinischen Befunde des Patienten einer Patientenkartei erhoben und gespeichert "
            "werden.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="14. DATENSCHUTZ\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Die folgende Einverständniserklärung zur Erhebung / Verarbeitung / Übermittlung der "
            "Klienten Daten ist Bestandteil dieser Vereinbarung. Ich bin damit einverstanden, dass meine "
            "Daten zum Zwecke der Dokumentation gespeichert werden. Die Therapeutin verpflichtet sich, die "
            "Daten außerhalb der notwendigen Eingaben zur Diagnose und Behandlung nicht an unbeteiligte "
            "Dritte weiterzugeben. Diese Erklärung ist jederzeit widerrufbar. Ich bin damit einverstanden "
            "Terminvereinbarungen, Übungsaufgaben, Tipps, Hinweise oder ähnliches ggf. auch über "
            "Plattformen wie z.B. WhatsApp, SMS, etc. auszutauschen, nützliche Informationen über Kurse, "
            "Veranstaltungen oder Neuigkeiten zu erhalten (z.B. Newsletter). Diese Erklärung ist "
            "jederzeit widerrufbar.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="15. GÜLTIGKEITSDAUER\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Die Vereinbarung gilt für alle weiteren und zukünftigen Sitzungen.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="16. ERFÜLLUNGSORT & GERICHTSSTAND\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Erfüllungsort und Gerichtsstand für alle Streitigkeiten ist München. Es gilt das Recht "
            "der Bundesrepublik Deutschland.",
        )

        self.ln(6)
        self.cell(175, 0, border=1, center=True)
        self.ln(2)

        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Ich willige hiermit nach ausreichender Bedenkzeit in die vorgeschlagene Behandlung ein. "
            "Eine Ausfertigung dieses Behandlungsvertrages habe ich erhalten",
        )

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

        self.output(filepath)
