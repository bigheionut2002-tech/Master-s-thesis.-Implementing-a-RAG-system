import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function Login() {
  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Sign in</CardTitle>
          <CardDescription>Access your RAG workspace.</CardDescription>
        </CardHeader>
        <CardContent>
          {/* TODO: email + password form wired to /auth/login */}
          <p className="text-sm text-muted-foreground">Login form — coming soon.</p>
        </CardContent>
      </Card>
    </div>
  )
}
