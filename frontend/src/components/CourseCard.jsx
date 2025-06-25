import React, { useEffect, useState } from "react"
import axios from "axios"

import { Link } from "react-router-dom"
import "./../styles/CourseCard.css"

export default function CourseCard({ course_id, title, date, students, user_role }) {
  const [materialCount, setMaterialCount] = useState(0)

  useEffect(() => {
    if (!course_id) return

    const token = localStorage.getItem("access_token")
    axios
      .get("/api/get_course_feed", {
        headers: { Authorization: `Bearer ${token}` },
        params: { course_id },
      })
      .then((res) => setMaterialCount(res.data.length))
      .catch((err) => {
        console.warn(`Could not load materials for course ${course_id}`, err.message)
        // optionally: setMaterialCount('?') or just leave 0
      })
  }, [course_id])

  return (
    <Link to={`/courses/${course_id}`} className="course-link-wrapper">
      <div className="course-card">
        <div className="course-card-banner">
          <span className="role-label">{user_role}</span>
        </div>
        <div className="course-card-content">
          <h3 className="course-title">{title}</h3>
          <p><strong>Created:</strong> {date}</p>
          <p><strong>Students:</strong> {students}</p>
          <p><strong>Materials:</strong> {materialCount}</p>
        </div>
      </div>
    </Link>
  )
}
