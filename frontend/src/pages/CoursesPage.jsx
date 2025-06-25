import React, { useEffect, useState } from "react"
import axios from "axios"

import CourseCard from "../components/CourseCard"
import "./../styles/CoursesPage.css"
import Header from "../components/Header"
import CreateCourseModal from "../components/CreateCourse"

export default function CoursesPage() {
  const [courses, setCourses] = useState([])
  const [showCreateCourseModal, setShowCreateCourseModal] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem("access_token")

    axios
      .get("/available_courses", {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then(async (res) => {
        const full = await Promise.all(
          res.data.map(async (c) => {
            const infoRes = await axios.get("/get_course_info", {
              headers: { Authorization: `Bearer ${token}` },
              params: { course_id: c.course_id },
            })

            const roleRes = await axios.get("/get_user_role", {
              headers: { Authorization: `Bearer ${token}` },
              params: { course_id: c.course_id },
            })

            const role = roleRes.data
            let user_role = "unknown"
            if (role.is_teacher) user_role = "teacher"
            else if (role.is_student) user_role = "student"
            else if (role.is_parent) user_role = "parent"

            return {
              ...infoRes.data,
              user_role,
            }
          })
        )

        setCourses(full)
      })
      .catch((err) => {
        console.error(err)
        alert("Session expired or failed to load courses")
        window.location.href = "/"
      })
  }, [courses])

  return (
    <Header>
      <div className="courses-page">
        <div className="courses-header">
        <h1>My Courses</h1>
        <button onClick={() => setShowCreateCourseModal(true)} className="create-course-page-button">+ Add Course</button>
        </div>

        <div className="course-list-grid">
          {courses.map((c) => (
            <CourseCard
              key={c.course_id}
              course_id={c.course_id}
              title={c.title}
              date={c.creation_time}
              students={c.number_of_students}
              user_role={c.user_role}
            />
          ))}
        </div>
      </div>
      {showCreateCourseModal && (
        <CreateCourseModal 
          onClose={() => setShowCreateCourseModal(false)}
        />
      )}
      
    </Header>
  )
}
