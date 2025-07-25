import React, { useEffect, useState } from "react"
import { Link, useLocation } from "react-router-dom"
import axios from "axios"
import CreateCourseModal from "../components/CreateCourse"
import { ReactComponent as Logo } from "./edHub_icon.svg"

import "../styles/Header.css"

export default function Header({ children }) {
  const [courses, setCourses] = useState([])
  const location = useLocation()
  const [showCreateCourseModal, setShowCreateCourseModal] = useState(false)

  const fetchCourses = async () => {
    const token = localStorage.getItem("access_token")
    try {
      const res = await axios.get("/api/available_courses", {
        headers: { Authorization: `Bearer ${token}` },
      })

      const detailed = await Promise.all(
        res.data.map(async (c) => {
          const info = await axios.get("/api/get_course_info", {
            headers: { Authorization: `Bearer ${token}` },
            params: { course_id: c.course_id },
          })
          return {
            course_id: c.course_id,
            title: info.data.title,
          }
        })
      )

      setCourses(detailed)
    } catch (err) {
      console.error("Failed to load full course list", err)
    }
  }

  useEffect(() => {
    fetchCourses()
  }, [])

  const courseMap = {}
  courses.forEach((c) => (courseMap[c.course_id] = c.title))

  const pathParts = location.pathname.split("/").filter(Boolean)

  const buildPath = (index) => {
    return "/" + pathParts.slice(0, index + 1).join("/")
  }

  function logout() {
    localStorage.setItem("access_token", "")
    window.location = window.origin
  }

  async function handleDeleteAccount() {
    if (!window.confirm("Are you sure you want to delete your account? This cannot be undone.")) return;
    try {
      const token = localStorage.getItem("access_token");
      await axios.post("/api/remove_user", null, {
        headers: { Authorization: `Bearer ${token}` },
      });
      localStorage.removeItem("access_token");
      window.location = window.origin;
    } catch (error) {
      console.error("Failed to delete account:", error);
      alert("Something went wrong while deleting your account.");
    }
  }


  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-title">
          <Logo className="sidebar-logo" onClick={()=>{window.location.assign(window.location.origin)}}/>
        </div>
        <div className="sidebar-section">Courses</div>
        <ul className="course-list">
          {courses.map((c) => {
            const active = location.pathname.includes(c.course_id)
            return (
              <li key={c.course_id}>
                <Link
                  to={`/courses/${c.course_id}`}
                  className={`course-link ${active ? "active" : ""}`}
                >
                  {c.title}
                </Link>
              </li>
            )
          })}
        </ul>
        <Link onClick={() => setShowCreateCourseModal(true)} className="create-course-link">
          + Create Course
        </Link>
        {showCreateCourseModal && (
          <CreateCourseModal
            onClose={() => setShowCreateCourseModal(false)}
            onCourseCreated={fetchCourses}
          />
        )}
     <div className="logout-btn-bottom" >
      <button className="logout-btn" onClick={logout}>Log out</button>
      <button className="delete-account-btn" onClick={handleDeleteAccount}>Delete Account</button>
    </div>

    </aside>
      <main className="main-content">
        <div className="breadcrumbs">
          {pathParts.map((segment, idx) => {
            const path = buildPath(idx)
            const isCourseId = segment.length > 20 && courseMap[segment]
            const label = isCourseId
              ? courseMap[segment]
              : segment.charAt(0).toUpperCase() + segment.slice(1)

            return (
              <span key={idx}>
                {idx > 0 && " / "}
                <Link to={path} className="breadcrumb-link">
                  {label}
                </Link>
              </span>
            )
          })}
        </div>

        <div className="content-wrapper">{children}</div>
      </main>
    </div>
  )
}
