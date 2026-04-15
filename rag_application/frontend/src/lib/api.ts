import axios, { type AxiosInstance } from "axios"

const AUTH_STORAGE_KEY = "rag-access-token"

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"

export const api: AxiosInstance = axios.create({
  baseURL,
  timeout: 30_000,
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
