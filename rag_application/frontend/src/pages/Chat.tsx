import { Send, Sparkles } from "lucide-react"
import { useEffect, useRef, useState, type FormEvent } from "react"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { apiQuery, extractErrorMessage, type SourceCitation } from "@/lib/api"
import { cn } from "@/lib/utils"

interface UserMessage {
  role: "user"
  id: string
  content: string
}

interface AssistantMessage {
  role: "assistant"
  id: string
  content: string
  sources: SourceCitation[]
}

type Message = UserMessage | AssistantMessage

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [draft, setDraft] = useState("")
  const [pending, setPending] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" })
  }, [messages, pending])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const question = draft.trim()
    if (question.length === 0 || pending) return

    const userMessage: UserMessage = {
      role: "user",
      id: crypto.randomUUID(),
      content: question,
    }
    setMessages((prev) => [...prev, userMessage])
    setDraft("")
    setPending(true)

    try {
      const response = await apiQuery(question)
      const assistantMessage: AssistantMessage = {
        role: "assistant",
        id: crypto.randomUUID(),
        content: response.answer,
        sources: response.sources,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: unknown) {
      toast.error(extractErrorMessage(error))
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col gap-4">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Chat</h1>
        <p className="text-sm text-muted-foreground">
          Ask a question and get an answer grounded in your uploaded PDFs.
        </p>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto rounded-lg border bg-card/40 p-6"
      >
        {messages.length === 0 && !pending ? <EmptyChatState /> : null}

        <div className="space-y-4">
          {messages.map((message) =>
            message.role === "user" ? (
              <UserBubble key={message.id} content={message.content} />
            ) : (
              <AssistantBubble
                key={message.id}
                content={message.content}
                sources={message.sources}
              />
            ),
          )}
          {pending ? <AssistantLoading /> : null}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          placeholder="Ask something about your documents…"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          disabled={pending}
        />
        <Button type="submit" disabled={pending || draft.trim().length === 0} className="gap-2">
          <Send className="h-4 w-4" />
          Send
        </Button>
      </form>
    </div>
  )
}

function EmptyChatState() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-muted">
        <Sparkles className="h-6 w-6 text-muted-foreground" />
      </div>
      <h3 className="text-base font-medium">Ask your first question</h3>
      <p className="max-w-md text-sm text-muted-foreground">
        Your question will be matched against the chunks from every document
        you uploaded, and the answer will be grounded in the retrieved excerpts.
      </p>
    </div>
  )
}

function UserBubble({ content }: { content: string }) {
  return (
    <div className="flex justify-end">
      <Card className="max-w-[85%] bg-primary text-primary-foreground">
        <CardContent className="whitespace-pre-wrap p-4 text-sm">{content}</CardContent>
      </Card>
    </div>
  )
}

interface AssistantBubbleProps {
  content: string
  sources: SourceCitation[]
}

function AssistantBubble({ content, sources }: AssistantBubbleProps) {
  return (
    <div className="flex justify-start">
      <Card className={cn("max-w-[85%]")}>
        <CardContent className="space-y-3 p-4">
          <p className="whitespace-pre-wrap text-sm leading-6">{content}</p>
          {sources.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {sources.map((source, index) => (
                <Badge key={`${source.filename}-${source.page}-${index}`} variant="secondary">
                  {source.filename} · p.{source.page}
                </Badge>
              ))}
            </div>
          ) : null}
        </CardContent>
      </Card>
    </div>
  )
}

function AssistantLoading() {
  return (
    <div className="flex justify-start">
      <Card className="w-[85%] max-w-xl">
        <CardContent className="space-y-2 p-4">
          <Skeleton className="h-4 w-4/5" />
          <Skeleton className="h-4 w-3/5" />
          <Skeleton className="h-4 w-2/3" />
        </CardContent>
      </Card>
    </div>
  )
}
