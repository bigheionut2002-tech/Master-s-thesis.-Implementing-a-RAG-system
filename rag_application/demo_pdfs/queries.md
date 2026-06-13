# Demo Evaluation Queries

These queries were used to evaluate the RAG system against the legal document corpus below.
Each query has a ground-truth answer verified manually against the source document.

## Documents in this corpus (Corpus A)

| File | Description |
|------|-------------|
| `contract_de_munca.pdf` | Individual employment contract (synthetically generated) |
| `regulament_intern_firma.pdf` | Internal company regulations (synthetically generated) |
| `contract_prestari_servicii.pdf` | Services provision contract (synthetically generated) |
| `contract_vanzare_cumparare_imobil.pdf` | Real estate sale-purchase contract (synthetically generated) |
| `notificare_juridica_gdpr.pdf` | GDPR legal notification (synthetically generated) |
| `acord_cooperare_test.pdf` | Commercial cooperation agreement — extended test document (synthetically generated) |

> All documents are **synthetically generated** for evaluation purposes and do not represent real legal entities or transactions.

---

## Factual queries

| # | Query (Romanian) | Source document | Ground-truth answer |
|---|-----------------|-----------------|---------------------|
| 1 | Care este perioada de probă pentru angajat? | `contract_de_munca.pdf` | 90 de zile calendaristice |
| 2 | Câte zile de concediu de odihnă are angajatul pe an? | `contract_de_munca.pdf` | 21 de zile lucrătoare |
| 3 | Care sunt obligațiile angajatorului conform contractului? | `contract_de_munca.pdf` | Plata salariului, asigurarea condițiilor de muncă |
| 4 | Care este termenul de preaviz în caz de demisie? | `regulament_intern_firma.pdf` | 20 de zile lucrătoare |
| 5 | Ce sancțiuni disciplinare sunt prevăzute în regulament? | `regulament_intern_firma.pdf` | Avertisment, reducerea salariului, desfacerea contractului |
| 6 | Care este termenul de plată conform contractului de prestări servicii? | `contract_prestari_servicii.pdf` | 30 de zile de la emiterea facturii |
| 7 | Ce date personale sunt prelucrate conform notificării GDPR? | `notificare_juridica_gdpr.pdf` | Nume, adresă, CNP, date de contact |
| 8 | Care sunt drepturile persoanelor vizate conform GDPR? | `notificare_juridica_gdpr.pdf` | Dreptul de acces, rectificare, ștergere, portabilitate |

## Cross-referential queries

| # | Query (Romanian) | Expected source passages |
|---|-----------------|--------------------------|
| 9 | Care sunt condițiile de încetare a contractului și ce preaviz se aplică? | `contract_de_munca.pdf` + `regulament_intern_firma.pdf` |
| 10 | Ce obligații are prestatorul și cum se soluționează litigiile? | `contract_prestari_servicii.pdf` |

## Numerical queries

| # | Query (Romanian) | Expected numeric answer |
|---|-----------------|------------------------|
| 11 | Câte zile calendaristice durează perioada de probă? | 90 |
| 12 | În câte zile trebuie achitată factura conform contractului de servicii? | 30 |
