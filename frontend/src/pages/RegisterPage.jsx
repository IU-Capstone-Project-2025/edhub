import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardTitle } from "@/components/ui/card"
import axios from "axios"
import { useNavigate } from "react-router-dom"

export default function RegisterPage() {
  const [email, setEmail] = useState("")
  const [name, setName] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const handleRegister = async () => {
    try {
      const res = await axios.post("/create_user", {
        email,
        password,
        name
      })
      localStorage.setItem("access_token", res.data.access_token)
      navigate("/courses")
    } catch (err) {
      alert("Ошибка регистрации: " + err.response?.data?.detail || err.message)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#f5f9ff]">
      <Card className="w-full max-w-md p-6 shadow-md">
        <CardTitle className="text-center mb-4 text-xl">EdHub LMS</CardTitle>
        <CardContent className="space-y-4">
          <h2 className="text-md font-semibold">Register</h2>
          <Input
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            placeholder="Your Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Input
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white" onClick={handleRegister}>
            Register
          </Button>
          <div className="text-right text-sm">
            <a href="/login" className="text-blue-600 hover:underline">Login</a>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
