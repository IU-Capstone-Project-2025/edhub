import React, { useState } from "react"
import axios from "axios"
import "../styles/AddGrade.css"

export default function AddGrade({ onClose, courseId ,assignmentId, studentEmail}) {
  const [loading, setLoading] = useState(false)
  const [assGrade, setAssGrade] = useState("")

  const handleSubmit = async () => {
    if (!studentEmail.trim() || !assignmentId.trim() || !courseId.trim()) {
      alert("Essential variables missing: Student's Email, Course ID, or Assignment ID")
      return
    }

    try {
        setLoading(true)
        const token = localStorage.getItem("access_token")
        if(!assGrade.trim() || assGrade < 1 || assGrade >10){
            alert("Assignment grade should be between 1-10 and shouldn't be null")
            setLoading(false)
            onClose()
            return
        }
        await axios.post("/api/grade_submission", null, {
            headers: {Authorization: `Bearer ${token}` },
            params:{student_email: studentEmail, course_id: courseId, assignment_id: assignmentId, grade: assGrade}
        })
        alert("Grade added successfully!")
        setLoading(false)
        onClose()
    } catch (err) {
        setLoading(false)
        const errorData = err.response?.data?.detail
        alert("Error adding grade: " + (
        typeof errorData === "string"
            ? errorData
            : JSON.stringify(errorData || err.message)
        ))
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Rate Submission</h2>
        <input
          type="text"
          placeholder="Rate Submission"
          value={assGrade}
          onChange={(e) => setAssGrade(e.target.value)}
        />
        <div className="modal-actions">
          <button className="cancel-btn" onClick={onClose} disabled={loading}>Cancel</button>
          <button onClick={handleSubmit} disabled={loading}>Rate</button>
        </div>
      </div>
    </div>
  )
}
