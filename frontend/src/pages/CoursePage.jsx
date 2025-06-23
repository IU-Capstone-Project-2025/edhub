import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import axios from "axios"

import "../styles/CoursePage.css"
import Header from "../components/Header"
import CourseFeed from "../components/CourseFeed"
import AddMaterial from "../components/AddMaterial"
import AddAssignment from "../components/AddAssignment"

export default function CoursePage() {
  const { id } = useParams()
  const [courseInfo, setCourseInfo] = useState(null)
  const [showMaterialModal, setShowMaterialModal] = useState(false)
  const [showAddAssignment, setShowAddAssignment] = useState(false)

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/get_course_info", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id },
        })
        setCourseInfo(res.data)
      } catch (err) {
        alert("Ошибка при загрузке курса: " + (err.response?.data?.detail || err.message))
      }
    }

    fetchCourse()
  }, [id])

  const handleAdd = (type) => {
    alert(`TODO: Добавить ${type} в курс`)
  }

  if (!courseInfo) return <div>Loading course...</div>

  return (
    <Header>
      <div className="course-page">
        <h1>{courseInfo.title}</h1>
        <p>Created: {courseInfo.creation_date}</p>
        <p>Students enrolled: {courseInfo.number_of_students}</p>

        <div className="actions">
          <button onClick={() => setShowMaterialModal(true)}>+ Add Material</button>
          <button onClick={() => setShowAddAssignment(true)}>+ Add Assignment</button>
          <button onClick={() => handleAdd("student")}>+ Add Student</button>
          <button onClick={() => handleAdd("teacher")}>+ Add Teacher</button>
          <button onClick={() => handleAdd("parent")}>+ Add Parent</button>
        </div>

        <CourseFeed />
      </div>

      {showMaterialModal && (
        <AddMaterial
          onClose={() => setShowMaterialModal(false)}
          courseId={id}
        />
      )}
      {showAddAssignment && (
        <AddAssignment
          onClose={() => setShowAddAssignment(false)}
          courseId={id}
        />
      )}
    </Header>
  )
}
