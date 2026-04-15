import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"

export function HowToUse() {
  return (
    <div className="mx-auto min-h-screen max-w-3xl p-6">
      <h1 className="mb-6 text-3xl font-semibold">Cum folosești aplicația</h1>
      <Card>
        <CardHeader>
          <CardTitle>Ghid rapid</CardTitle>
          <CardDescription>
            Patru pași simpli ca să obții primul răspuns din documentele tale.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6 text-sm leading-6">
          <section>
            <h2 className="mb-2 text-base font-medium">1. Încarcă un PDF</h2>
            <p className="text-muted-foreground">
              Mergi la <strong>Documente</strong> și apasă <em>Upload</em>. Alege un fișier
              PDF — aplicația îl extrage, îl împarte în fragmente și îl indexează automat.
              Limită: un fișier pe rând, maxim 20&nbsp;MB.
            </p>
          </section>

          <Separator />

          <section>
            <h2 className="mb-2 text-base font-medium">2. Pune o întrebare</h2>
            <p className="text-muted-foreground">
              Deschide pagina <strong>Chat</strong> și scrie o întrebare în limbaj natural,
              de exemplu: <em>„Care este perioada de probă în contractul colectiv?”</em>
            </p>
          </section>

          <Separator />

          <section>
            <h2 className="mb-2 text-base font-medium">3. Citește răspunsul și sursele</h2>
            <p className="text-muted-foreground">
              Răspunsul este generat de model folosind doar fragmentele relevante din
              documentele tale. Sub răspuns apar <strong>badge-uri</strong> cu fișierul și
              pagina exactă de unde a fost extrasă fiecare informație — apasă pe ele ca să
              verifici sursa.
            </p>
          </section>

          <Separator />

          <section>
            <h2 className="mb-2 text-base font-medium">4. Limitări</h2>
            <ul className="list-disc space-y-1 pl-6 text-muted-foreground">
              <li>Se acceptă doar fișiere PDF (fără Word, Excel sau scanări cu OCR).</li>
              <li>Fișierele tale sunt izolate — nu sunt vizibile altor utilizatori.</li>
              <li>
                Modelul poate greși. Folosește badge-urile cu sursele pentru verificare.
              </li>
            </ul>
          </section>
        </CardContent>
      </Card>
    </div>
  )
}
