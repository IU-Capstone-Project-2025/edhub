import React, { useState } from "react"
import "./../styles/AuthPage.css"
import noavatar from "../components/edHub_icon.svg";
import axios from "axios"

import { useNavigate } from "react-router-dom"

export default function AuthPage() {
  const [email, setEmail] = useState("")
  const [name, setName] = useState("")
  const [password, setPassword] = useState("")
  const [isLogin, setIsLogin] = useState(true)
  const [error, setError] = useState("")
  const navigate = useNavigate()

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  function validatePassword(pw) {
    return pw.length >= 8 && /[a-zA-Z]/.test(pw) && /\d/.test(pw)
  }

  const handleSubmit = async () => {
  setError("");

  if (!email || !password || (!isLogin && !name)) {
    setError("Please fill in all required fields.");
    return;
  }

  if (!emailRegex.test(email)) {
    setError("Please enter a valid email address.");
    return;
  }

  if (!validatePassword(password)) {
    setError("Password must be at least 8 characters long and include at least one letter and one number.");
    return;
  }

  try {
    const endpoint = isLogin ? "/api/login" : "/api/create_user";
    const payload = isLogin ? { email, password } : { email, password, name };
    const res = await axios.post(endpoint, payload);

    localStorage.setItem("access_token", res.data.access_token);
    navigate("/courses");
  } catch (err) {
    const msg = err.response?.data?.detail || "Unknown error";

    if (msg.includes("Invalid user email")) {
      setError("No user found with this email. Please check or sign up first.");
    } else if (msg.includes("Invalid password")) {
      setError("Incorrect password. Please try again.");
    } else if (msg.includes("already exists")) {
      setError("A user with this email already exists.");
    } else {
      setError(msg);
    }
  }
};



  return (
    <div className="auth-page">
      <div className="auth-gradient" />

      <div className="auth-content">
        <div className="auth-left">
          <div className="auth-logo">
            <img className="logo-image" src={noavatar} alt="No avatar" width={200} height={100} />
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

          <form onSubmit={(e) => e.preventDefault()} noValidate>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            {!isLogin && (
              <input
                type="text"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                pattern="^[A-Za-zА-Яа-яёЁ\s]{2,}$"
                title="Please enter your full name (at least 2 letters)."
                required
              />
            )}
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              pattern="^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
              title="Password must be at least 8 characters long and include at least one letter and one number."
              required
            />
            <button type="submit" onClick={handleSubmit}>
              {isLogin ? "Log In" : "Sign Up"}
            </button>
          </form>

          {error && <div className="form-error">{error}</div>}

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
