import React, { useState } from "react"
import axios from "axios"

import { useNavigate } from "react-router-dom"
import "./../styles/CreateCourse.css"
import { ToastContainer, toast } from "react-toastify"
import "react-toastify/dist/ReactToastify.css"

export default function CreateCourseModal({ onClose }) {
  const [title, setTitle] = useState("")
  const navigate = useNavigate()

  const handleCreate = async () => {
    try {
      const token = localStorage.getItem("access_token")
      await axios.post(`/api/create_course?title=${encodeURIComponent(title)}`, null, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      toast.success("Course created!", {
        position: "bottom-right",
      })

      onClose() // Закрываем модалку
      navigate("/courses")
    } catch (err) {
      toast.error("Failed: " + (err.response?.data?.detail || err.message), {
        position: "bottom-right",
      })
    }
  }

  return (
    <div className="modal-backdrop">
      <div className="create-course-page modal">
        <h1>Create a New Course</h1>
        <input
          type="text"
          placeholder="Course title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <button onClick={handleCreate}>Create Course</button>
        <button onClick={onClose} style={{ marginTop: 10, backgroundColor: "#ccc", color: "#333" }}>
          Cancel
        </button>
      </div>
      <ToastContainer />
    </div>
  )
}
