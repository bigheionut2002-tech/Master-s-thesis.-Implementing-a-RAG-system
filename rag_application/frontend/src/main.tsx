import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter } from "react-router-dom"
import { Toaster } from "sonner"

import App from "./App.tsx"
import { AuthProvider } from "./components/auth-provider.tsx"
import { ThemeProvider } from "./components/theme-provider.tsx"
import "./index.css"

const rootElement = document.getElementById("root")
if (rootElement === null) {
  throw new Error("Root element #root not found in index.html")
}

createRoot(rootElement).render(
  <StrictMode>
    <ThemeProvider defaultTheme="dark" storageKey="rag-ui-theme">
      <BrowserRouter>
        <AuthProvider>
          <App />
          <Toaster richColors position="top-right" />
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  </StrictMode>,
)
