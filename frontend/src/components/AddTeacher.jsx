import React, { useState } from "react"
import axios from "axios"
import "../styles/AddTeacher.css"

export default function AddTeacher({ onClose, courseId }) {
  const [teacherEmail, setTeacherEmail] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!teacherEmail.trim()) {
      alert("Teacher's Email is required")
      return
    }

    try {
      setLoading(true)
      const token = localStorage.getItem("access_token")
      const form = new URLSearchParams()
      form.append("course_id", courseId)
      form.append("new_teacher_email", teacherEmail)

await axios.post("/api/invite_teacher", form, {
        headers: {Authorization: `Bearer ${token}` },
        params:{new_teacher_email: teacherEmail, course_id: courseId}
      })
      alert("Teacher added successfully!")
      setTeacherEmail("")
      setLoading(false)
      onClose()
    } catch (err) {
      setLoading(false)
      const errorData = err.response?.data?.detail
      alert("Error adding teacher: " + (
        typeof errorData === "string"
          ? errorData
          : JSON.stringify(errorData || err.message)
      ))
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Add Teacher</h2>
        <input
          type="text"
          placeholder="Teacher Email"
          value={teacherEmail}
          onChange={(e) => setTeacherEmail(e.target.value)}
          onKeyDown={(e)=>(e.code==="Enter" ? handleSubmit(e) : null)}
        />
        <div className="modal-actions">
          <button className="cancel-btn" onClick={onClose} disabled={loading}>Cancel</button>
          <button className="outlined-btn" onClick={handleSubmit} disabled={loading}>Add</button>
        </div>
      </div>
    </div>
  )
}
