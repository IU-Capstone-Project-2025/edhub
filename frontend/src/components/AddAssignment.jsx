import React, { useState } from "react"
import axios from "axios"
import "../styles/AddMaterial.css" 

export default function AddAssignment({ onClose, courseId }) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!title.trim() || !description.trim()) {
      alert("Title and description are required")
      return
    }

    try {
      const token = localStorage.getItem("access_token")
      const form = new URLSearchParams()
      form.append("course_id", courseId)
      form.append("title", title)
      form.append("description", description)

      await axios.post(
        `/api/create_assignment?course_id=${courseId}&title=${encodeURIComponent(title)}&description=${encodeURIComponent(description)}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      setTitle("")
      setDescription("")
      setLoading(false)

      onSuccess?.()
      onClose()
    } catch (err) {
      setLoading(false)
      const errorData = err.response?.data?.detail
      alert("Ошибка при добавлении ассаймента: " + (
        typeof errorData === "string"
          ? errorData
          : JSON.stringify(errorData || err.message)
      ))
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Add Assignment</h2>
        <input
          type="text"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <textarea
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <div className="modal-actions">
          <button className="cancel-btn" onClick={onClose} disabled={loading}>Cancel</button>
          <button onClick={handleSubmit} disabled={loading}>Add</button>
        </div>
      </div>
    </div>
  )
}
