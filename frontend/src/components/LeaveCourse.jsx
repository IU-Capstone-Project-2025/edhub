import React, { useState } from "react"
import axios from "axios"
import "../styles/AddStudent.css"



export default function LeaveCourse({ onClose, courseId , roleData, ownEmail}) {
  const [loading, setLoading] = useState(false)
  const [childrenArray, setChildrenArray] = useState([])
  

  const role = roleData.is_teacher
  ? "teacher"
  : roleData.is_student
  ? "student"
  : roleData.is_parent
  ? "parent"
  : "unknown";
  const handleSubmit = async () => {
    if (!ownEmail.trim()) {
      alert("Your Email didn't load, try reloading the page")
      return
    }

    try {
        setLoading(true)
        const token = localStorage.getItem("access_token")
        switch (role) {
          case "teacher":
            const teachersRes = await axios.get("/api/get_course_teachers", {
                headers: {Authorization: `Bearer ${token}` },
                params:{course_id: courseId}
            })
            if ( teachersRes.data.length > 1) {
                await axios.post("/api/remove_teacher", null, {
                    headers: {Authorization: `Bearer ${token}` },
                    params:{removing_teacher_email: ownEmail, course_id: courseId}
                })
            }else{
                alert("You are the only teacher in this course. You cannot leave it.")
                setLoading(false)
                onClose()
                return
            }
            break
          case "student":
            await axios.post("/api/remove_student", null, {
                headers: {Authorization: `Bearer ${token}` },
                params:{student_email: ownEmail, course_id: courseId}
            })
            break
          case "parent":
            const res = await axios.get("/api/get_parents_children",{
                headers: {Authorization: `Bearer ${token}` },
                params:{course_id: courseId}
            })
            setChildrenArray(res.data)
            const student_email = res.data[0]?.email
            await axios.post("/api/remove_parent", null, {
                headers: {Authorization: `Bearer ${token}` },
                params:{parent_email: ownEmail, course_id: courseId, student_email}
            })
            break
          default:
            alert("Failed to fetch role data")
            break
        }
        alert("You left the course successfully!")
        setLoading(false)
        onClose()
    } catch (err) {
      setLoading(false)
      const errorData = err.response?.data?.detail
      alert("Ошибка при удалении : " + (
        typeof errorData === "string"
          ? errorData
          : JSON.stringify(errorData || err.message)
      ))
    }
  }
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Leave the course</h2>
        <p>Are you sure you want to leave this course?</p>
        <p>This action cannot be undone.</p>
        <p>Role: {role}</p>
        <p>Your Email: {ownEmail}</p>
        <p>Course ID: {courseId}</p>
        <div className="modal-actions">
          <button className="cancel-btn" onClick={onClose} disabled={loading}>Cancel</button>
          <button onClick={handleSubmit} disabled={loading}>Leave</button>
        </div>
      </div>
    </div>
  )
}
