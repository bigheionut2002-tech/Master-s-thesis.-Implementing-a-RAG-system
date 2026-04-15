import { Navigate, Route, Routes } from "react-router-dom"

import { ProtectedRoute } from "./components/protected-route"
import { Chat } from "./pages/Chat"
import { Dashboard } from "./pages/Dashboard"
import { HowToUse } from "./pages/HowToUse"
import { Landing } from "./pages/Landing"
import { Login } from "./pages/Login"
import { Register } from "./pages/Register"

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/how-to-use" element={<HowToUse />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
