import React, { useState } from "react"
import axios from "axios"
import "../styles/DeleteCourse.css"



export default function DeleteCourse({ onClose, courseId}) {
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = async () => {
    if (!courseId.trim()) {
      alert("CourseId didn't load, try reloading the page")
      return
    }

    try {
        setLoading(true)
        const token = localStorage.getItem("access_token")
        await axios.post("/api/remove_course", null, {
            headers: {Authorization: `Bearer ${token}` },
            params:{course_id: courseId}
        })
        window.location.assign("../courses")
    } catch (err) {
      setLoading(false)
      const errorData = err.response?.data?.detail
      alert("Error while removing: " + (
        typeof errorData === "string"
          ? errorData
          : JSON.stringify(errorData || err.message)
      ))
    }
  }
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Delete the course</h2>
        <p>Are you sure you want to delete this course?</p>
        <p>This action cannot be undone.</p>
        <div className="modal-actions">
          <button className="cancel-btn" onClick={onClose} disabled={loading}>Cancel</button>
          <button onClick={handleSubmit} disabled={loading}>Delete</button>
        </div>
      </div>
    </div>
  )
}
