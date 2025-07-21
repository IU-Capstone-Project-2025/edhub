import React, { useState, useRef, useEffect } from "react"
import axios from "axios"
import "../styles/AddMaterial.css"

export default function AddMaterial({ onClose, courseId, onSuccess  }) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({ title: false, description: false })


  const titleRef = useRef(null)

  useEffect(() => {
    titleRef.current?.focus()
  }, [])

  const handleSubmit = async () => {
    const titleEmpty = !title.trim()
    const descEmpty = !description.trim()
    setErrors({ title: titleEmpty, description: descEmpty })
    if (titleEmpty || descEmpty) return

    try {
      setLoading(true)
      const token = localStorage.getItem("access_token")
      const form = new URLSearchParams()
      form.append("course_id", courseId)
      form.append("title", title)
      form.append("description", description)

await axios.post("/api/create_material", form, {
        headers: {Authorization: `Bearer ${token}` },
        params:{title, description, course_id: courseId}
      })
      setTitle("")
      setDescription("")
      setErrors({ title: false, description: false })

      setLoading(false)
      onSuccess?.()
      onClose()
    } catch (err) {
      setLoading(false)
      const errorData = err.response?.data?.detail
      alert("Error adding material: " + (
        typeof errorData === "string"
          ? errorData
          : JSON.stringify(errorData || err.message)
      ))
    }
  }

    const handleTitleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Add Material</h2>
        <input
          ref={titleRef}
          type="text"
          placeholder="Title"
          value={title}
          onChange={(e) => {
            setTitle(e.target.value)
            setErrors((prev) => ({ ...prev, title: false }))
          }}
          onKeyDown={handleTitleKeyDown}
        />
        {errors.title && <div className="error-message">Title is required</div>}

        <textarea
          placeholder="Description"
          value={description}
          onChange={(e) => {
            setDescription(e.target.value)
            setErrors((prev) => ({ ...prev, description: false }))
          }}
        />
        {errors.description && <div className="error-message">Description is required</div>}

        <div className="modal-actions">
          <button className="cancel-btn" onClick={onClose} disabled={loading}>Cancel</button>
          <button className="outlined-btn" onClick={handleSubmit} disabled={loading}>Add</button>
        </div>
      </div>
    </div>
  )
}
