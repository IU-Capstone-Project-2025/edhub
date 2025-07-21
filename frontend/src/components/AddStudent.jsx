import React, { useState, useRef, useEffect } from "react"
import axios from "axios"
import "../styles/AddStudent.css"

export default function AddStudent({ onClose, courseId }) {
  const [studentEmail, setStudentEmail] = useState("")
  const [loading, setLoading] = useState(false)
  const inputRef = useRef(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSubmit = async () => {
    if (!studentEmail.trim()) {
      alert("Student's Email is required")
      return
    }

    try {
      setLoading(true)
      const token = localStorage.getItem("access_token")
      const form = new URLSearchParams()
      form.append("course_id", courseId)
      form.append("student_email", studentEmail)

await axios.post("/api/invite_student", form, {
        headers: {Authorization: `Bearer ${token}` },
        params:{student_email: studentEmail, course_id: courseId}
      })
      alert("Student added successfully!")
      setStudentEmail("")
      setLoading(false)
      onClose()
    } catch (err) {
      setLoading(false)
      const errorData = err.response?.data?.detail
      alert("Error adding student: " + (
        typeof errorData === "string"
          ? errorData
          : JSON.stringify(errorData || err.message)
      ))
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Add Student</h2>
        <input
          ref={inputRef}
          type="text"
          placeholder="Student Email"
          value={studentEmail}
          onChange={(e) => setStudentEmail(e.target.value)}
          onKeyDown={(e) => e.code === "Enter" && handleSubmit()}
        />
        <div className="modal-actions">
          <button className="cancel-btn" onClick={onClose} disabled={loading}>Cancel</button>
          <button className="outlined-btn" onClick={handleSubmit} disabled={loading}>Add</button>
        </div>
      </div>
    </div>
  )
}
