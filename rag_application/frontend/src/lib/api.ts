import axios, { AxiosError, type AxiosInstance } from "axios"

const AUTH_STORAGE_KEY = "rag-access-token"

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"

export const api: AxiosInstance = axios.create({
  baseURL,
  timeout: 60_000,
  headers: {
    "Content-Type": "application/json",
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(AUTH_STORAGE_KEY)
  if (token !== null && config.headers !== undefined) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export function storeAccessToken(token: string): void {
  localStorage.setItem(AUTH_STORAGE_KEY, token)
}

export function clearAccessToken(): void {
  localStorage.removeItem(AUTH_STORAGE_KEY)
}

export function getAccessToken(): string | null {
  return localStorage.getItem(AUTH_STORAGE_KEY)
}

export interface UserPublic {
  id: number
  email: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface DocumentMetadata {
  id: string
  filename: string
  num_pages: number
  num_chunks: number
}

export interface SourceCitation {
  filename: string
  page: number
}

export interface QueryResponse {
  answer: string
  sources: SourceCitation[]
}

export function extractErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail
    if (typeof detail === "string") return detail
    if (Array.isArray(detail)) {
      return detail.map((d) => d?.msg ?? String(d)).join(", ")
    }
    return error.message
  }
  if (error instanceof Error) return error.message
  return "Unexpected error"
}

export async function apiRegister(email: string, password: string): Promise<UserPublic> {
  const { data } = await api.post<UserPublic>("/auth/register", { email, password })
  return data
}

export async function apiLogin(email: string, password: string): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/login", { email, password })
  return data
}

export async function apiMe(): Promise<UserPublic> {
  const { data } = await api.get<UserPublic>("/auth/me")
  return data
}

export async function apiListDocuments(): Promise<DocumentMetadata[]> {
  const { data } = await api.get<DocumentMetadata[]>("/documents")
  return data
}

export async function apiUploadDocument(file: File): Promise<DocumentMetadata> {
  const form = new FormData()
  form.append("file", file)
  const { data } = await api.post<DocumentMetadata>("/documents/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return data
}

export async function apiDeleteDocument(documentId: string): Promise<void> {
  await api.delete(`/documents/${documentId}`)
}

export async function apiQuery(question: string): Promise<QueryResponse> {
  const { data } = await api.post<QueryResponse>("/query", { question })
  return data
}
