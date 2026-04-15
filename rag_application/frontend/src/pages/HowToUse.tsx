import { FileText, MessageSquare, ShieldCheck, Sparkles } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"

export function HowToUse() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Cum folosești aplicația</h1>
        <p className="text-sm text-muted-foreground">
          Un ghid scurt pentru cineva care folosește aplicația pentru prima dată.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Ce face aplicația</CardTitle>
          <CardDescription>
            Pe scurt: încarci documente PDF, pui întrebări în limbaj natural,
            primești răspunsuri fundamentate pe sursele din propriile tale fișiere.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm leading-6 text-muted-foreground">
          <p>
            Aplicația citește textul fiecărui PDF pe care îl încarci, îl împarte în
            fragmente mici, calculează o reprezentare matematică a înțelesului lor
            (<em>embedding</em>) și o stochează într-o bază de date vectorială. Când
            pui o întrebare, sistemul caută fragmentele cele mai apropiate semantic,
            le trimite ca și context unui model de limbaj și îți returnează un
            răspuns împreună cu sursele exacte (fișier și pagină).
          </p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <StepCard
          icon={<FileText className="h-5 w-5" />}
          step="Pasul 1"
          title="Încarcă un PDF"
          description="Mergi la pagina Documents și apasă Upload PDF. Alege un fișier — aplicația îl procesează automat și îl indexează. Limita este de 20 MB per fișier. Merg doar PDF-uri cu text (nu scanări)."
        />
        <StepCard
          icon={<MessageSquare className="h-5 w-5" />}
          step="Pasul 2"
          title="Pune o întrebare"
          description='Deschide pagina Chat și scrie o întrebare în limbaj natural, de exemplu: „Care este perioada de probă conform contractului?"'
        />
        <StepCard
          icon={<Sparkles className="h-5 w-5" />}
          step="Pasul 3"
          title="Citește răspunsul și sursele"
          description="Răspunsul este generat doar pe baza fragmentelor relevante din documentele tale. Sub răspuns apar badge-uri cu numele fișierului și pagina exactă. Dacă un răspuns nu se află în documente, aplicația îți spune clar acest lucru."
        />
        <StepCard
          icon={<ShieldCheck className="h-5 w-5" />}
          step="Pasul 4"
          title="Documentele tale sunt izolate"
          description="Fiecare utilizator are propria colecție de documente. Nici un alt utilizator nu poate vedea sau interoga fișierele tale. Poți șterge un document oricând din pagina Documents."
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Limitări</CardTitle>
          <CardDescription>Lucruri de știut înainte de a folosi aplicația pentru ceva important.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-6 text-muted-foreground">
          <ul className="list-disc space-y-1 pl-6">
            <li>Se acceptă doar PDF-uri cu strat de text. Scanările fără OCR sunt ignorate.</li>
            <li>Maxim 20 MB per fișier încărcat.</li>
            <li>
              Modelul poate greși în cazuri rare. Folosește întotdeauna badge-urile
              cu sursele pentru a verifica răspunsul.
            </li>
            <li>
              Răspunsurile sunt generate prin API-ul Gemini. În timpul utilizării
              intensive, modelul poate avea latențe ușor mai mari.
            </li>
          </ul>
          <Separator className="my-4" />
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-muted-foreground">Tag-uri:</span>
            <Badge variant="secondary">RAG</Badge>
            <Badge variant="secondary">Vector Database</Badge>
            <Badge variant="secondary">ChromaDB</Badge>
            <Badge variant="secondary">Google Gemini</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

interface StepCardProps {
  icon: React.ReactNode
  step: string
  title: string
  description: string
}

function StepCard({ icon, step, title, description }: StepCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-foreground">
            {icon}
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              {step}
            </p>
            <CardTitle className="text-base">{title}</CardTitle>
          </div>
        </div>
      </CardHeader>
      <CardContent className="text-sm leading-6 text-muted-foreground">{description}</CardContent>
    </Card>
  )
}
