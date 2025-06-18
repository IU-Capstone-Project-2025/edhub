import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import axios from "axios"
import { useNavigate } from "react-router-dom"

export default function AuthPage() {
  const [email, setEmail] = useState("")
  const [name, setName] = useState("")
  const [password, setPassword] = useState("")
  const [isLogin, setIsLogin] = useState(true)
  const navigate = useNavigate()

  const handleSubmit = async () => {
    try {
      const endpoint = isLogin ? "/login" : "/create_user"
      const payload = isLogin ? { email, password } : { email, password, name }

      const res = await axios.post(endpoint, payload)
      localStorage.setItem("access_token", res.data.access_token)
      navigate("/courses")
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message))
    }
  }

  return (
    <div className="min-h-screen bg-white flex flex-col w-full">
      <div className="h-[30vh] w-full bg-gradient-to-b from-[#3BBF12] via-[#4CB050] to-transparent" />

      <div className="flex-1 w-full flex justify-center px-4">
        <div className="w-full max-w-[90%] flex flex-col md:flex-row items-center justify-between gap-12">
         
          <div className="w-full md:w-[50%] text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start gap-2 mb-6 relative w-fit">
              <h1 className="text-5xl font-bold text-[#333940]">
                ed
                <span className="relative inline-block">
                  H
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 64 40"
                    className="absolute -top-6 left-0 w-8 h-6"
                    fill="#4CB050"
                  >
                    <polygon points="32,0 64,10 32,20 0,10" />
                    <line x1="32" y1="20" x2="32" y2="35" stroke="#4CB050" strokeWidth="4" />
                  </svg>
                </span>
                ub
              </h1>
            </div>

            <p className="text-gray-600 text-lg max-w-[90%] md:max-w-[75%] mx-auto md:mx-0">
              EdHub is a modern learning platform that helps students, teachers, and parents manage courses, share materials, and stay connected — all in one place.
            </p>
          </div>

          <div className="w-full md:w-[40%] bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-800 text-center mb-2">
              {isLogin ? "Log In" : "Sign Up"}
            </h2>
            <p className="text-center text-gray-400 mb-6">
              {isLogin
                ? "Access your learning dashboard"
                : "Create a new EdHub account"}
            </p>

            <div className="space-y-4">
              <Input
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-gray-100"
              />
              {!isLogin && (
                <Input
                  placeholder="Full Name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="bg-gray-100"
                />
              )}
              <Input
                placeholder="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-gray-100"
              />

              <Button
              className="w-full bg-[#4CB050] hover:bg-[#3BBF12] text-white text-md rounded-xl py-3 border-2 border-transparent hover:border-[#2E7D32] transition"
                onClick={(e) => {
                  e.currentTarget.blur()
                  handleSubmit()
                }}
              >
                {isLogin ? "Log In" : "Sign Up"}
              </Button>

              <div className="text-center text-sm mt-2">
                <button
                  onClick={(e) => { setIsLogin(!isLogin)
                    e.currentTarget.blur()
                  }}
                className="text-[#4CB050] hover:underline font-medium border-2 border-transparent hover:border-[#2E7D32] rounded-md px-2 py-1 transition"
                >
                  {isLogin
                    ? "Don't have an account? Sign up"
                    : "Already have an account? Log in"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
