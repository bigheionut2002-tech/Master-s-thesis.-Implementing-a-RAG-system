import { ArrowRight, Sparkles } from "lucide-react"
import { Suspense } from "react"
import { Link, Navigate } from "react-router-dom"

import { useAuth } from "@/components/auth-provider"
import { Button } from "@/components/ui/button"
import R3fBlob from "@/components/ui/r3f-blob"

export function Landing() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-sm text-muted-foreground">Loading…</div>
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground">
      <div className="pointer-events-none absolute inset-0">
        <Suspense fallback={null}>
          <R3fBlob />
        </Suspense>
      </div>

      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-background/60 via-background/10 to-background/80" />

      <header className="relative z-10 mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2 text-lg font-semibold tracking-tight">
          <Sparkles className="h-5 w-5" />
          RAG System
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login">
            <Button variant="ghost" size="sm">
              Sign in
            </Button>
          </Link>
          <Link to="/register">
            <Button size="sm">Get started</Button>
          </Link>
        </div>
      </header>

      <section className="relative z-10 mx-auto flex min-h-[calc(100vh-96px)] w-full max-w-3xl flex-col items-center justify-center px-6 text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border bg-card/60 px-3 py-1 text-xs text-muted-foreground backdrop-blur">
          <span className="h-1.5 w-1.5 rounded-full bg-foreground" />
          Information retrieval over your own documents
        </div>

        <h1 className="mb-6 text-balance text-4xl font-semibold tracking-tight md:text-6xl">
          Ask your PDFs.
          <br />
          Get answers with sources.
        </h1>

        <p className="mb-10 max-w-xl text-pretty text-base text-muted-foreground md:text-lg">
          A Retrieval-Augmented Generation system built on a vector database.
          Upload your documents, ask questions in natural language, and see
          exactly which page the answer came from.
        </p>

        <div className="flex flex-col items-center gap-3 sm:flex-row">
          <Link to="/register">
            <Button size="lg" className="gap-2">
              Create an account
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link to="/login">
            <Button size="lg" variant="outline">
              Sign in
            </Button>
          </Link>
        </div>

        <p className="mt-8 text-xs text-muted-foreground">
          Demo accounts: <code className="rounded bg-muted px-1 py-0.5">avocatura@demo.com</code>,{" "}
          <code className="rounded bg-muted px-1 py-0.5">restaurant@demo.com</code>,{" "}
          <code className="rounded bg-muted px-1 py-0.5">admin@demo.com</code> — password{" "}
          <code className="rounded bg-muted px-1 py-0.5">demo1234</code>
        </p>
      </section>

      <footer className="relative z-10 mx-auto w-full max-w-6xl px-6 pb-6 text-center text-xs text-muted-foreground">
        Master&apos;s thesis · Babeș-Bolyai University, Cluj-Napoca · 2025–2026
      </footer>
    </div>
  )
}
