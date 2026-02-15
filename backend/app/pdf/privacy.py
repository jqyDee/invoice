from .document_pdf import DocumentPdf

class Privacy(DocumentPdf):
    """Creates the HP PDF and outputs to given filepath"""

    # setting pdf font sizes
    header_font_size = 10
    normal_font_size = 8
    privacy_font_size = 7

    rechnungsempfaenger_offset = 4
    default_offset = 6
    in_text_offset = 3

    def __init__(
        self,
        stammdaten: list,
        filepath: str,
    ):
        super().__init__("Datenschutzinformation und Einwilligungserklärung")

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
        self.write(text="Datenschutzinformation und Einwilligungserklärung")
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

        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "In meiner Praxis werden während Ihrer Behandlung personenbezogene vertrauliche Daten erhoben."
            " Immer schon unterliegen alle Therapeuten und Mitarbeiter in meiner Praxis einer strengen "
            "Schweigepflicht. Nach dem jetzt in Kraft getretenen neuen Datenschutzrecht "
            "(EU-Datenschutz-Grundverordnung und Bundesdatenschutzgesetz) sind wir verpflichtet, Sie "
            "darüber zu informieren, zu welchem Zweck meine Praxis Daten erhebt, speichert oder "
            "weiterleitet. Der Information können Sie auch entnehmen, welche Rechte Sie beim Datenschutz "
            "haben. Ferner ist Ihre ausdrückliche Einwilligung in die Datenerhebung erforderlich. Dies "
            "bezieht sich auch auf unsere Angebote, wie z.B. Kurse, Seminare oder Vorlesungen außerhalb "
            "der Praxis.",
        )
        self.ln(self.default_offset)
        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="1. VERANTWORTLICHKEIT FÜR DIE DATENVERARBEITUNG\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.write(text="Verantwortlich für die Datenverarbeitung ist:\n")
        self.write(text="Mervi Fischbach\n")
        self.write(text="Heilpraktikerin\n")
        self.write(text="Schulgasse 9 - 86923 Finning\n")
        self.write(text="Telefon: 08806 / 9587111\n")
        self.write(text="E-Mail: mervi.winter@web.de")
        self.ln(self.default_offset)
        self.write(
            text="In unserem Bundesland ist in allen Datenschutzangelegenheiten Ansprechpartner:\n"
        )
        self.write(text="Dr. Thomas Petri\n")
        self.write(text="Wagmüllerstraße 18 - 80538 München\n")
        self.write(text="Telefon: 089 / 212672-0\n")
        self.write(text="E-Mail: poststelle@datenschutz-bayern.de")
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="2. ZWECK DER DATENVERARBEITUNG\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Die Datenverarbeitung erfolgt aufgrund gesetzlicher Vorgaben, um den Behandlungsvertrag "
            "zwischen Ihnen und Ihrem Heilpraktiker und die damit verbundenen "
            "Pflichten zu erfüllen. Hierzu verarbeite ich Ihre personenbezogenen Daten, insbesondere Ihre "
            "Gesundheitsdaten. Dazu zählen Anamnesen, Diagnosen, Therapievorschläge und Befunde, die ich "
            "oder andere Heilpraktiker erheben. Zu diesen Zwecken können uns auch andere Heilpraktiker, "
            "Ärzte, Psychologische Psychotherapeuten und Physiotherapeuten bei denen Sie in Behandlung "
            "sind, Daten zur Verfügung stellen (z. B. in Therapeutenbriefen), wenn Sie sie von Ihrer "
            "Schweigepflicht entbunden haben. Die Erhebung von Gesundheitsdaten ist Voraussetzung für "
            "Ihre Behandlung. Werden die notwendigen Informationen nicht bereitgestellt, kann eine "
            "sorgfältige Behandlung nicht erfolgen.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="3. WEITERGABE IHRER DATEN AN DRITTE\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Ich übermittele Ihre personenbezogenen Daten nur dann an Dritte (z. B. ein Labor), wenn "
            "Sie eingewilligt haben.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="4. SPEICHERUNG IHRER DATEN\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Ich bewahren Ihre personenbezogenen Daten nur solange auf, wie dies für die Durchführung "
            "der Behandlung erforderlich ist. Nach rechtlichen Vorgaben sind ich dazu verpflichtet, diese "
            "Daten mindestens 10 Jahre nach Abschluss der Behandlung aufzubewahren.",
        )
        self.ln(self.default_offset)

        self.add_page()
        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="5. EINWILLIGUNGSERKLÄRUNGN\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Durch Ihre Unterschrift erklären Sie sich ausdrücklich mit der für Ihre Behandlung "
            "notwendigen Erhebung und Speicherung persönlicher Daten einverstanden. Sie haben das Recht, "
            "diese Einwilligung jederzeit zu widerrufen, jedoch wirkt ein Widerruf nur für die Zukunft, da "
            "nach gesetzlichen Bestimmungen eine Dokumentation Ihrer Behandlungsdaten zwingend "
            "vorgeschrieben ist. Nach Widerruf dieser Einwilligungserklärung ist allerdings eine weitere "
            "Behandlung nicht mehr möglich.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="6. WEITERE EINWILLIGUNGSERKLÄRUNGEN\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Einverständnis, Informationen, Terminvereinbarungen, Übungsaufgaben, Tipps, Hinweise oder "
            "ähnliches ggf. auch über per E-Mail, WhatsApp, Messenger, Post, etc. zu erhalten, bzw. "
            "auszutauschen.",
        )
        self.ln(self.in_text_offset)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Einverständnis, Informationen, Tipps, Hinweise (z.B. zur Gesundheit, "
            "Praxisveranstaltungen) oder ähnliches per Newsletter zu erhalten.",
        )
        self.ln(self.in_text_offset)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Einverständnis, Sitzungen über Telefon oder Onlineplattformen zu machen falls "
            "gewünscht/vereinbart (z.B. über SKYPE).",
        )
        self.ln(self.in_text_offset)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Betrifft nur Kurse, Seminare und Veranstaltungen: Einverständnis, dass Foto oder Video "
            "Aufnahmen ohne Namensnennung im Rahmen unserer Öffentlichkeitsarbeit, z.B. Werbung, "
            "Internetseiten Verwendung finden dürfen.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="7. IHRE RECHTE\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Sie haben das Recht, über die Sie betreffenden personenbezogenen Daten Auskunft zu erhalten. "
            "Auch können Sie die Berichtigung unrichtiger Daten verlangen. Darüber hinaus steht Ihnen "
            "unter bestimmten Voraussetzungen das Recht auf Löschung von Daten, das Recht auf "
            "Einschränkung der Datenverarbeitung sowie das Recht auf Datenübertragbarkeit zu.",
        )
        self.ln(self.in_text_offset)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Die Verarbeitung Ihrer Daten erfolgt auf Basis von gesetzlichen Regelungen. Nur in "
            "Ausnahmefällen benötigen wir Ihr Einverständnis. In diesen Fällen haben Sie das Recht, die "
            "Einwilligung für die zukünftige Verarbeitung zu widerrufen.",
        )
        self.ln(self.in_text_offset)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Sie haben ferner das Recht, sich bei der zuständigen Aufsichtsbehörde für den "
            "Datenschutz zu beschweren, wenn Sie der Ansicht sind, dass die Verarbeitung Ihrer "
            "personenbezogenen Daten nicht rechtmäßig erfolgt.",
        )
        self.ln(self.in_text_offset)
        self.multi_cell(
            0,
            self.normal_font_size / 2.5,
            "Die Anschrift des für unsere Praxis zuständigen Datenschutzbeauftragen/Aufsichtsbehörde "
            "können Sie oben Nr. 1. entnehmen.",
        )
        self.ln(self.default_offset)

        self.set_font("helvetica", "B", self.header_font_size)
        self.write(text="8. RECHTLICHE GRUNDLAGEN\n")
        self.set_font("helvetica", size=self.normal_font_size)
        self.multi_cell(
            0,
            self.normal_font_size / 3,
            "Rechtsgrundlage für die Verarbeitung Ihrer Daten ist Artikel 9 Absatz 2 lit. h) DS-GVO in "
            "Verbindung mit § 22 Absatz 1 Nr. 1 lit. b) Bundesdatenschutzgesetz. Sollten Sie Fragen haben, "
            "können Sie sich jederzeit an mich wenden.",
        )
        self.ln(self.default_offset)

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
