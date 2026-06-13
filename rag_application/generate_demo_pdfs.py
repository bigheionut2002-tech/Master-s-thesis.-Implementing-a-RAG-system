"""Generate 5 demo legal PDFs for RAG testing."""

import fitz  # PyMuPDF


def make_pdf(filename: str, title: str, sections: list[tuple[str, str]]) -> None:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4

    y = 60
    # Title
    page.insert_text((50, y), title, fontsize=16, fontname="helv")
    y += 30
    page.draw_line((50, y), (545, y), color=(0, 0, 0), width=0.5)
    y += 20

    for heading, body in sections:
        if y > 750:
            page = doc.new_page(width=595, height=842)
            y = 60

        page.insert_text((50, y), heading, fontsize=11, fontname="helv")
        y += 18

        words = body.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 > 90:
                if y > 800:
                    page = doc.new_page(width=595, height=842)
                    y = 60
                page.insert_text((50, y), line, fontsize=9, fontname="helv")
                y += 14
                line = word
            else:
                line = (line + " " + word).strip()
        if line:
            if y > 800:
                page = doc.new_page(width=595, height=842)
                y = 60
            page.insert_text((50, y), line, fontsize=9, fontname="helv")
            y += 14
        y += 10

    doc.save(filename)
    doc.close()
    print(f"Created: {filename}")


# --- 1: Contract de Munca ---
make_pdf(
    "contract_de_munca.pdf",
    "CONTRACT INDIVIDUAL DE MUNCA",
    [
        ("Partile contractante", (
            "Angajator: SC IUREX LEGAL SRL, Cluj-Napoca, str. Eroilor nr. 5, "
            "J12/1234/2020, CIF RO12345678, reprezentata de dl. Andrei Popescu - Administrator."
        )),
        ("Art. 1 - Obiectul contractului", (
            "Prezentul contract reglementeaza raporturile de munca conform Legii nr. 53/2003 "
            "- Codul Muncii, republicat, cu modificarile si completarile ulterioare."
        )),
        ("Art. 2 - Durata contractului", (
            "Contractul se incheie pe durata nedeterminata incepand cu data de 01.07.2025. "
            "Perioada de proba este de 90 de zile calendaristice pentru functii de executie "
            "si 120 de zile calendaristice pentru functii de conducere, conform art. 31 Codul Muncii."
        )),
        ("Art. 3 - Locul de munca", (
            "Salariatul isi desfasoara activitatea la sediul angajatorului din Cluj-Napoca, "
            "str. Eroilor nr. 5. Angajatorul poate dispune detasarea cu acordul salariatului."
        )),
        ("Art. 4 - Felul muncii", (
            "Salariatul ocupa functia de Consilier Juridic, cod COR 261103, cu atributiile "
            "din Fisa postului, parte integranta din prezentul contract."
        )),
        ("Art. 5 - Programul de munca", (
            "Durata muncii este de 8 ore/zi, 40 ore/saptamana, luni-vineri, orele 09:00-17:00. "
            "Salariatul beneficiaza de o pauza de masa de 30 de minute inclusa in program."
        )),
        ("Art. 6 - Salariul", (
            "Salariul de baza lunar brut este de 8.000 lei. Plata se efectueaza lunar pana la "
            "data de 10 ale lunii urmatoare. Retinerile din salariu sunt permise numai in "
            "cazurile prevazute de lege."
        )),
        ("Art. 7 - Concediul de odihna", (
            "Durata concediului de odihna anual este de 21 de zile lucratoare. Concediul se "
            "efectueaza in fiecare an calendaristic. Efectuarea in anul urmator este permisa "
            "doar in cazurile expres prevazute de lege sau contractul colectiv de munca."
        )),
        ("Art. 8 - Obligatiile salariatului", (
            "Salariatul trebuie sa realizeze norma de munca; sa respecte disciplina muncii; "
            "sa respecte regulamentul intern si contractul individual de munca; sa fie loial "
            "angajatorului; sa respecte secretul de serviciu; sa nu presteze activitati "
            "concurente pe durata contractului."
        )),
        ("Art. 9 - Clauza de confidentialitate", (
            "Partile convin sa nu transmita date sau informatii de care au luat cunostinta "
            "pe durata contractului si timp de 2 ani dupa incetarea acestuia, in conditiile "
            "stabilite in regulamentele interne si contractele colective de munca."
        )),
        ("Art. 10 - Incetarea contractului", (
            "Contractul inceteaza: de drept; prin acordul partilor; prin vointa unilaterala. "
            "Preavizul la demisie este de 20 de zile lucratoare pentru executie si 45 de zile "
            "pentru conducere. Angajatorul acorda preaviz de 20 de zile lucratoare la concediere."
        )),
        ("Semnatura angajator", "_________________________ Data: 01.07.2025"),
        ("Semnatura salariat", "_________________________ Data: 01.07.2025"),
    ]
)

# --- 2: Contract de Vanzare-Cumparare Imobil ---
make_pdf(
    "contract_vanzare_cumparare_imobil.pdf",
    "CONTRACT DE VANZARE-CUMPARARE IMOBIL",
    [
        ("Partile contractante", (
            "VANZATOR: Ionescu Alexandru, CNP 1850312123456, Cluj-Napoca, str. Avram Iancu nr. 12. "
            "CUMPARATOR: Georgescu Maria, CNP 2900615654321, Bucuresti, str. M. Eminescu nr. 45."
        )),
        ("Art. 1 - Obiectul contractului", (
            "Vanzatorul vinde cumparatoarei imobilul din Cluj-Napoca, str. Memorandumului nr. 8, "
            "ap. 5, compus din 3 camere, suprafata utila 78 mp, CF nr. 123456 Cluj-Napoca, "
            "nr. cadastral 78901."
        )),
        ("Art. 2 - Pretul vanzarii", (
            "Pretul convenit este de 120.000 euro. Cumparatoarea a achitat avans de 24.000 euro "
            "conform chitantei nr. 001/15.05.2025. Diferenta de 96.000 euro se plateste la "
            "autentificare prin virament in IBAN RO49AAAA1B31007593840000 deschis la Banca Transilvania."
        )),
        ("Art. 3 - Garantii privind imobilul", (
            "Vanzatorul garanteaza: imobilul este proprietatea sa exclusiva; nu este grevat de "
            "sarcini, ipoteci sau privilegii; nu exista litigii; taxele si impozitele sunt "
            "achitate la zi; imobilul nu face obiectul unui contract de inchiriere."
        )),
        ("Art. 4 - Predarea imobilului", (
            "Predarea se face la data autentificarii, pe baza unui proces-verbal de predare-primire. "
            "Imobilul va fi liber de locatari si predat cu toate cheile, documentele tehnice "
            "si certificatul de performanta energetica."
        )),
        ("Art. 5 - Evictiunea si viciile ascunse", (
            "Vanzatorul raspunde de evictiunea totala sau partiala si de viciile ascunse, "
            "conform Codului Civil. Garantia contra viciilor ascunse este de 3 ani de la "
            "data predarii imobilului."
        )),
        ("Art. 6 - Cheltuielile contractului", (
            "Cheltuielile notariale si de intabulare se suporta de cumparatoare. "
            "Impozitul pe venit din transfer se suporta de vanzator conform Codului Fiscal."
        )),
        ("Art. 7 - Litigii", (
            "Orice litigiu se solutioneaza pe cale amiabila. In caz de esec, partile se "
            "adreseaza instantelor judecatoresti competente din Cluj-Napoca."
        )),
        ("Semnatura vanzator", "_________________________ Data: 15.06.2025"),
        ("Semnatura cumparator", "_________________________ Data: 15.06.2025"),
        ("Notar public", "_________________________ Data: 15.06.2025"),
    ]
)

# --- 3: Regulament Intern ---
make_pdf(
    "regulament_intern_firma.pdf",
    "REGULAMENT INTERN - SC IUREX LEGAL SRL",
    [
        ("Cap. I - Dispozitii generale", (
            "Art. 1. Prezentul Regulament este elaborat conform art. 241-246 Codul Muncii. "
            "Stabileste regulile privind securitatea in munca, drepturile si obligatiile "
            "angajatorului si salariatilor, procedura de solutionare a reclamatiilor si "
            "sanctiunile disciplinare."
        )),
        ("Art. 2 - Domeniu de aplicare", (
            "Se aplica tuturor salariatilor societatii, indiferent de durata contractului "
            "sau functia ocupata, inclusiv persoanelor detasate."
        )),
        ("Cap. II - Timpul de munca", (
            "Art. 3. Durata normala a timpului de lucru este de 8 ore pe zi si 40 de ore pe "
            "saptamana, de luni pana vineri intre 09:00-17:00. Munca suplimentara se compenseaza "
            "prin ore libere sau prin spor de 75% la salariu."
        )),
        ("Art. 4 - Pauze", (
            "Salariatii beneficiaza de 30 de minute pauza de masa inclusa in program. "
            "Repausul saptamanal: sambata si duminica. Sarbatorile legale conform Codul Muncii."
        )),
        ("Cap. III - Concedii", (
            "Art. 5. Concediul de odihna anual platit este de minim 21 zile lucratoare. "
            "Programarea se face la inceputul anului. Concediul medical conform OUG nr. 158/2005. "
            "Concediul de maternitate este de 126 zile calendaristice conform legii."
        )),
        ("Art. 6 - Absente nemotivate", (
            "Absenta nemotivata constituie abatere disciplinara. Salariatul care nu se prezinta "
            "este obligat sa anunte seful ierarhic in cel mult 2 ore de la inceperea programului."
        )),
        ("Cap. IV - Disciplina muncii", (
            "Art. 7. Sanctiunile disciplinare sunt: avertisment scris; retrogradare din functie "
            "maximum 60 de zile; reducerea salariului cu 5-10% pe 1-3 luni; desfacerea "
            "disciplinara a contractului de munca."
        )),
        ("Art. 8 - Procedura disciplinara", (
            "Nicio sanctiune cu exceptia avertismentului nu se aplica fara cercetare disciplinara "
            "prealabila, finalizata in maximum 30 de zile calendaristice. Salariatul are dreptul "
            "de a fi audiat si de a prezenta dovezi in apararea sa."
        )),
        ("Cap. V - Protectia datelor GDPR", (
            "Art. 9. Prelucrarea datelor salariatilor respecta Regulamentul (UE) nr. 679/2016. "
            "Salariatii au drept de acces, rectificare, stergere si portabilitate a datelor. "
            "Datele se stocheaza pe durata contractului si 5 ani ulterior."
        )),
        ("Art. 10 - Confidentialitate", (
            "Salariatii sunt obligati sa pastreze confidentialitatea informatiilor de serviciu. "
            "Obligatia se mentine 2 ani dupa incetarea raportului de munca."
        )),
        ("Cap. VI - Dispozitii finale", (
            "Art. 11. Regulamentul a fost adoptat in sedinta din 01.01.2025 si intra in vigoare "
            "la data afisarii la sediul societatii. Modificarile se comunica salariatilor cu "
            "minimum 15 zile inainte."
        )),
    ]
)

# --- 4: Contract de Prestari Servicii ---
make_pdf(
    "contract_prestari_servicii.pdf",
    "CONTRACT DE PRESTARI SERVICII JURIDICE",
    [
        ("Partile contractante", (
            "PRESTATOR: CABINET AVOCAT MIHAI STANESCU, Cluj-Napoca, Piata Unirii nr. 3, "
            "Baroul Cluj nr. 456, CIF 23456789. "
            "BENEFICIAR: SC TECH SOLUTIONS SRL, Cluj-Napoca, str. Observatorului nr. 91, "
            "CUI RO34567890, reprezentata prin Radu Ionescu - Director General."
        )),
        ("Art. 1 - Obiectul contractului", (
            "Prestatorul se obliga sa presteze servicii juridice: consultanta in dreptul comercial, "
            "dreptul muncii si dreptul fiscal; redactarea si avizarea contractelor; reprezentarea "
            "in fata instantelor; asistenta la negocieri si mediere; opinii juridice la solicitare."
        )),
        ("Art. 2 - Durata contractului", (
            "Contractul se incheie pe 12 luni, 01.06.2025 - 31.05.2026, cu reinnoire automata "
            "daca niciuna din parti nu notifica rezilierea cu 30 de zile inainte de expirare."
        )),
        ("Art. 3 - Onorariul", (
            "Onorariu lunar fix: 5.000 lei + TVA, platibil pana la 15 ale lunii. "
            "Reprezentarea in instanta si actele complexe se factureaza suplimentar prin acte "
            "aditionale. Intarzierea la plata atrage penalitati de 0,1% pe zi de intarziere."
        )),
        ("Art. 4 - Obligatiile prestatorului", (
            "Prestatorul se obliga sa: acorde consultanta in maximum 48 ore lucratoare; "
            "respecte confidentialitatea informatiilor; informeze clientul despre modificari "
            "legislative relevante; asigure reprezentare calificata si diligenta in instanta."
        )),
        ("Art. 5 - Obligatiile beneficiarului", (
            "Beneficiarul se obliga sa: furnizeze informatiile si documentele necesare; "
            "achite onorariul la termen; notifice prestatorul despre riscuri litigioase; "
            "coopereze cu buna-credinta la solutionarea problemelor juridice."
        )),
        ("Art. 6 - Confidentialitate", (
            "Partile nu vor divulga tertilor informatiile si documentele schimbate fara acordul "
            "scris al celeilalte parti. Obligatia de confidentialitate se mentine 5 ani "
            "dupa incetarea contractului."
        )),
        ("Art. 7 - Forta majora", (
            "Nicio parte nu raspunde pentru neexecutare cauzata de forta majora. "
            "Partea care o invoca notifica cealalta parte in termen de 5 zile."
        )),
        ("Art. 8 - Incetarea contractului", (
            "Contractul inceteaza prin: expirare; acordul partilor; reziliere cu preaviz 30 zile. "
            "La neachitarea onorariului doua luni consecutive, prestatorul poate rezilia de plin drept. "
            "La incetare, prestatorul preda dosarele si documentele originale."
        )),
        ("Semnatura prestator", "_________________________ Data: 01.06.2025"),
        ("Semnatura beneficiar", "_________________________ Data: 01.06.2025"),
    ]
)

# --- 5: Politica GDPR ---
make_pdf(
    "notificare_juridica_gdpr.pdf",
    "POLITICA DE CONFIDENTIALITATE SI GDPR",
    [
        ("1. Introducere", (
            "SC IUREX LEGAL SRL, Cluj-Napoca, str. Eroilor nr. 5, CUI RO12345678, in calitate de "
            "Operator de date, prelucreaza datele personale cu respectarea Regulamentului (UE) "
            "nr. 679/2016 (GDPR) si legislatiei nationale. Prezenta politica descrie tipurile de "
            "date colectate, scopurile prelucrarii si drepturile dumneavoastra."
        )),
        ("2. Datele prelucrate", (
            "Prelucram: date de identificare (nume, CNP, data nasterii); date de contact "
            "(adresa, telefon, email); date financiare (IBAN, venituri); date referitoare la "
            "litigii si situatii juridice; corespondenta cu clientii."
        )),
        ("3. Scopurile prelucrarii", (
            "Datele sunt prelucrate pentru: executarea contractului de asistenta juridica "
            "(art. 6 alin. 1 lit. b GDPR); respectarea obligatiilor legale, ex. fiscale "
            "(art. 6 alin. 1 lit. c GDPR); interesul legitim - prevenirea fraudei "
            "(art. 6 alin. 1 lit. f GDPR); consimtamant pentru marketing (art. 6 alin. 1 lit. a)."
        )),
        ("4. Durata stocarii", (
            "Datele contractuale: 5 ani dupa incetarea contractului (termen de prescriptie). "
            "Documente contabile: 10 ani conform legislatiei fiscale. Date bazate pe consimtamant: "
            "sterse la retragerea consimtamantului sau expirarea scopului."
        )),
        ("5. Drepturile persoanelor vizate", (
            "Aveti dreptul la: acces la datele dumneavoastra (art. 15 GDPR); rectificare "
            "(art. 16 GDPR); stergere - dreptul de a fi uitat (art. 17 GDPR); restrictionarea "
            "prelucrarii (art. 18 GDPR); portabilitate (art. 20 GDPR); opozitie (art. 21 GDPR). "
            "Cererile se transmit la gdpr@iurex.ro sau in scris la sediu."
        )),
        ("6. Transferuri internationale", (
            "Nu transferam date in afara Spatiului Economic European. Daca utilizarea unor "
            "furnizori cloud din tari terte devine necesara, garantam transferul prin clauze "
            "contractuale standard aprobate de Comisia Europeana, conform Cap. V GDPR."
        )),
        ("7. Masuri de securitate", (
            "Aplicam: criptare in tranzit (TLS 1.3) si in repaus (AES-256); control acces "
            "bazat pe roluri; audit periodic al accesului; instruire personal; backup si "
            "recuperare date; plan de raspuns la incidente de securitate (breach notification "
            "in 72 ore catre ANSPDCP, conform art. 33 GDPR)."
        )),
        ("8. Contact DPO", (
            "Responsabilul cu protectia datelor (DPO): dpo@iurex.ro | Tel: 0264-123-456 | "
            "Sediu: Cluj-Napoca, str. Eroilor nr. 5. Puteti depune plangere la ANSPDCP, "
            "Bucuresti, B-dul G-ral Gheorghe Magheru nr. 28-30."
        )),
    ]
)

print("\nDone! 5 PDF files created.")
print("Upload them to the demo account at http://localhost:5173")
