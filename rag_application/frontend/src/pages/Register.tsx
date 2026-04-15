import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function Register() {
  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Create account</CardTitle>
          <CardDescription>Register to start uploading documents.</CardDescription>
        </CardHeader>
        <CardContent>
          {/* TODO: email + password form wired to /auth/register */}
          <p className="text-sm text-muted-foreground">Register form — coming soon.</p>
        </CardContent>
      </Card>
    </div>
  )
}
