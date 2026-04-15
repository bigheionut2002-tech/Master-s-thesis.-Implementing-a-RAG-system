import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function Dashboard() {
  return (
    <div className="mx-auto min-h-screen max-w-5xl p-6">
      <h1 className="mb-6 text-3xl font-semibold">Documents</h1>
      <Card>
        <CardHeader>
          <CardTitle>Your library</CardTitle>
          <CardDescription>Upload PDFs and manage your indexed documents.</CardDescription>
        </CardHeader>
        <CardContent>
          {/* TODO: document list + upload dialog wired to /documents */}
          <p className="text-sm text-muted-foreground">No documents yet.</p>
        </CardContent>
      </Card>
    </div>
  )
}
