import { FileText, Plus, Trash2, Upload } from "lucide-react"
import { useEffect, useState, type ChangeEvent } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import {
  apiDeleteDocument,
  apiListDocuments,
  apiUploadDocument,
  extractErrorMessage,
  type DocumentMetadata,
} from "@/lib/api"

export function Dashboard() {
  const [documents, setDocuments] = useState<DocumentMetadata[] | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const loadDocuments = async () => {
    try {
      const result = await apiListDocuments()
      setDocuments(result)
    } catch (error: unknown) {
      toast.error(extractErrorMessage(error))
      setDocuments([])
    }
  }

  useEffect(() => {
    loadDocuments()
  }, [])

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null
    setSelectedFile(file)
  }

  const handleUpload = async () => {
    if (selectedFile === null) {
      toast.error("Select a PDF first")
      return
    }
    setUploading(true)
    try {
      const metadata = await apiUploadDocument(selectedFile)
      toast.success(`Uploaded ${metadata.filename} (${metadata.num_chunks} chunks)`)
      setIsDialogOpen(false)
      setSelectedFile(null)
      await loadDocuments()
    } catch (error: unknown) {
      toast.error(extractErrorMessage(error))
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (doc: DocumentMetadata) => {
    setDeletingId(doc.id)
    try {
      await apiDeleteDocument(doc.id)
      toast.success(`Deleted ${doc.filename}`)
      await loadDocuments()
    } catch (error: unknown) {
      toast.error(extractErrorMessage(error))
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Documents</h1>
          <p className="text-sm text-muted-foreground">
            Upload PDFs to make them searchable. Each document is indexed per page.
          </p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Upload PDF
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Upload a PDF</DialogTitle>
              <DialogDescription>
                Select a PDF file from your computer. Maximum size: 20 MB.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-3 py-2">
              <Label htmlFor="pdf-file">File</Label>
              <input
                id="pdf-file"
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="block w-full text-sm text-muted-foreground file:mr-3 file:rounded-md file:border-0 file:bg-primary file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary-foreground hover:file:bg-primary/90"
              />
              {selectedFile !== null ? (
                <p className="text-xs text-muted-foreground">
                  {selectedFile.name} · {(selectedFile.size / 1024).toFixed(0)} KB
                </p>
              ) : null}
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setIsDialogOpen(false)
                  setSelectedFile(null)
                }}
                disabled={uploading}
              >
                Cancel
              </Button>
              <Button onClick={handleUpload} disabled={uploading || selectedFile === null}>
                {uploading ? (
                  "Ingesting…"
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload
                  </>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {documents === null ? (
        <DocumentsSkeleton />
      ) : documents.length === 0 ? (
        <EmptyState onUpload={() => setIsDialogOpen(true)} />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {documents.map((doc) => (
            <Card key={doc.id} className="flex flex-col">
              <CardHeader>
                <div className="flex items-start gap-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-primary/10">
                    <FileText className="h-5 w-5 text-foreground" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <CardTitle className="truncate text-base">{doc.filename}</CardTitle>
                    <CardDescription>
                      {doc.num_pages} {doc.num_pages === 1 ? "page" : "pages"} · {doc.num_chunks} chunks
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex-1" />
              <CardFooter>
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-2"
                  onClick={() => handleDelete(doc)}
                  disabled={deletingId === doc.id}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  {deletingId === doc.id ? "Deleting…" : "Delete"}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

function DocumentsSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[0, 1, 2].map((i) => (
        <Card key={i}>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Skeleton className="h-10 w-10 rounded-md" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            </div>
          </CardHeader>
          <CardFooter>
            <Skeleton className="h-8 w-20" />
          </CardFooter>
        </Card>
      ))}
    </div>
  )
}

interface EmptyStateProps {
  onUpload: () => void
}

function EmptyState({ onUpload }: EmptyStateProps) {
  return (
    <Card className="border-dashed">
      <CardContent className="flex flex-col items-center gap-4 py-16 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-muted">
          <FileText className="h-7 w-7 text-muted-foreground" />
        </div>
        <div className="space-y-1">
          <h3 className="text-base font-medium">No documents yet</h3>
          <p className="max-w-md text-sm text-muted-foreground">
            Upload your first PDF to start asking questions about its contents.
          </p>
        </div>
        <Button onClick={onUpload} className="gap-2">
          <Plus className="h-4 w-4" />
          Upload your first PDF
        </Button>
      </CardContent>
    </Card>
  )
}
