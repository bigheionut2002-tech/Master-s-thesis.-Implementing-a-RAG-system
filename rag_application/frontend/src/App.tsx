import { Navigate, Route, Routes } from "react-router-dom"

import { Chat } from "./pages/Chat"
import { Dashboard } from "./pages/Dashboard"
import { HowToUse } from "./pages/HowToUse"
import { Login } from "./pages/Login"
import { Register } from "./pages/Register"

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="/how-to-use" element={<HowToUse />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App
