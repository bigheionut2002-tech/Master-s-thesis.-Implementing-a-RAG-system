import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function Chat() {
  return (
    <div className="mx-auto min-h-screen max-w-4xl p-6">
      <h1 className="mb-6 text-3xl font-semibold">Ask your documents</h1>
      <Card>
        <CardHeader>
          <CardTitle>Chat</CardTitle>
          <CardDescription>
            Ask a question and get an answer grounded in your uploaded PDFs.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* TODO: chat input, answer stream, source badges wired to /query */}
          <p className="text-sm text-muted-foreground">Chat UI — coming soon.</p>
        </CardContent>
      </Card>
    </div>
  )
}
