import React, { useState } from "react"
import "./../styles/AuthPage.css"
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
    <div className="auth-page">
      <div className="auth-gradient" />

      <div className="auth-content">
        <div className="auth-left">
          <div className="auth-logo">
            <span className="ed">ed</span>
            <span className="hub">
              H
              <svg viewBox="0 0 64 40" className="hat">
                <polygon points="32,0 64,10 32,20 0,10" />
                <line x1="32" y1="20" x2="32" y2="35" stroke="#4CB050" strokeWidth="4" />
              </svg>
              ub
            </span>
          </div>
          <h1>Fast, Efficient and Productive</h1>
          <p>
            EdHub is a modern learning platform that helps students, teachers, and parents manage courses, share materials, and stay connected — all in one place.
          </p>
        </div>

        <div className="auth-form">
          <h2>{isLogin ? "Log In" : "Sign Up"}</h2>
          <p className="form-subtext">
            {isLogin ? "Access your learning dashboard" : "Create a new EdHub account"}
          </p>

          <form onSubmit={(e) => e.preventDefault()}>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            {!isLogin && (
              <input
                type="text"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            )}
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit" onClick={handleSubmit}>
              {isLogin ? "Log In" : "Sign Up"}
            </button>
          </form>

          <div className="form-toggle">
            <span onClick={() => setIsLogin(!isLogin)}>
              {isLogin ? "Don't have an account? Sign up" : "Already have an account? Log in"}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
