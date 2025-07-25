import React, { useEffect, useState } from "react"
import axios from "axios"
import PageMeta from "../components/PageMeta"
import CourseCard from "../components/CourseCard"
import "./../styles/CoursesPage.css"
import Header from "../components/Header"
import CreateCourseModal from "../components/CreateCourse"

export default function CoursesPage() {
  const [courses, setCourses] = useState([])
  const [showCreateCourseModal, setShowCreateCourseModal] = useState(false)

  const fetchCourses = async () => {
    const token = localStorage.getItem("access_token")
    try {
      const admins = await axios.get("/api/get_admins", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const user = await axios.get("/api/get_user_info", {
        headers: { Authorization: `Bearer ${token}` },
      });
      // if (admins.data.includes(user.data)) {
      //   const res = await axios.get("/api/available_courses", {
      //     headers: { Authorization: `Bearer ${token}` },
      //   });
      // }else{
      //   const res = await axios.get("/api/available_courses", {
      //     headers: { Authorization: `Bearer ${token}` },
      //   });
      // }
      const isAdmin = admins.data.some(admin => admin.email === user.data.email);
      const res = isAdmin
      ? await axios.get("/api/get_all_courses", {
          headers: { Authorization: `Bearer ${token}` },
        })
      : await axios.get("/api/available_courses", {
          headers: { Authorization: `Bearer ${token}` },
        });
      const full = await Promise.all(
        res.data.map(async (c) => {
          const infoRes = await axios.get("/api/get_course_info", {
            headers: { Authorization: `Bearer ${token}` },
            params: { course_id: c.course_id },
          });
          const roleRes = await axios.get("/api/get_user_role", {
            headers: { Authorization: `Bearer ${token}` },
            params: { course_id: c.course_id },
          });
          const role = roleRes.data
          let user_role = "unknown"
          if (role.is_admin) user_role = "admin"
          else if (role.is_student) user_role = "student"
          else if (role.is_parent) user_role = "parent"
          else if (role.is_teacher) user_role = "teacher"
          return {
            ...infoRes.data,
            user_role,
          }
        })
      );
      setCourses(full);
    } catch (err) {
      console.error(err)
      alert("Session expired or failed to load courses")
      window.location.href = "/"
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  return (
    <Header>
      <PageMeta title="Courses" icon="/edHub_icon.svg" />
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
          onCourseCreated={fetchCourses}
        />
      )}
    </Header>
  )
}
