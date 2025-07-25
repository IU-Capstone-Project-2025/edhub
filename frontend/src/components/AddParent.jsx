import React, { useState, useRef, useEffect } from "react"
import axios from "axios"
import "../styles/AddParent.css"

export default function AddParent({ onClose, courseId }) {
  const [studentEmail, setStudentEmail] = useState("")
  const [parentEmail, setParentEmail] = useState("")
  const [loading, setLoading] = useState(false)
  const studentInputRef = useRef(null)

  useEffect(() => {
    studentInputRef.current?.focus()
  }, [])


  const handleSubmit = async () => {
    if (!parentEmail.trim() || !studentEmail.trim()) {
      alert("Both parent's and student's emails are required")
      return
    }

    try {
      setLoading(true)
      const token = localStorage.getItem("access_token")
      const form = new URLSearchParams()
      form.append("course_id", courseId)
      form.append("student_email", studentEmail)
      form.append("parent_email", parentEmail)

await axios.post("/api/invite_parent", form, {
        headers: {Authorization: `Bearer ${token}` },
        params:{parent_email: parentEmail, course_id: courseId, student_email: studentEmail}
      })
      alert("Parent added successfully!")
      setStudentEmail("")
      setParentEmail("")
      setLoading(false)
      onClose()
    } catch (err) {
      setLoading(false)
      const errorData = err.response?.data?.detail
      alert("Error adding parent: " + (
        typeof errorData === "string"
          ? errorData
          : JSON.stringify(errorData || err.message)
      ))
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Add Parent</h2>
        <input
          ref={studentInputRef}
          type="text"
          placeholder="Student Email"
          value={studentEmail}
          onChange={(e) => setStudentEmail(e.target.value)}
        />
        <input
          type="text"
          placeholder="Parent Email"
          value={parentEmail}
          onChange={(e) => setParentEmail(e.target.value)}
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
