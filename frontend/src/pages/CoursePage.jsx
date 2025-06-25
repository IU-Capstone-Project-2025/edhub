import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import axios from "axios"

import "../styles/CoursePage.css"
import Header from "../components/Header"
import CourseFeed from "../components/CourseFeed"
import AddMaterial from "../components/AddMaterial"
import AddAssignment from "../components/AddAssignment"
import AddStudent from "../components/AddStudent"
import AddTeacher from "../components/AddTeacher"
import AddParent from "../components/AddParent"

export default function CoursePage() {
  const { id } = useParams()
  const [courseInfo, setCourseInfo] = useState(null)
  const [showMaterialModal, setShowMaterialModal] = useState(false)
  const [showAddAssignment, setShowAddAssignment] = useState(false)
  const [showAddStudent, setShowAddStudent] = useState(false)
  const [showAddTeacher, setShowAddTeacher] = useState(false)
  const [showAddParent, setShowAddParent] = useState(false)
  const [roleData, setRoleData] = useState()

  

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

    const fetchRoleData = async () => {
      try {
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/get_user_role", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id },
        })
        setRoleData(res.data)
      } catch (err) {
        alert("Ошибка при загрузке роли пользователя: " + (err.response?.data?.detail || err.message))
      }
    }
    fetchRoleData()
  }, [id])

  // const handleAdd = (type) => {
  //   alert(`TODO: Добавить ${type} в курс`)
  // }

  if (!courseInfo) return <div>Loading course...</div>

  return (
    <Header>
      <div className="course-page">
        <h1>{courseInfo.title}</h1>
        <p>Created: {courseInfo.creation_date}</p>
        <p>Students enrolled: {courseInfo.number_of_students}</p>
        {roleData && roleData.is_teacher && (
          <div className="actions">
            <button onClick={() => setShowMaterialModal(true)}>+ Add Material</button>
            <button onClick={() => setShowAddAssignment(true)}>+ Add Assignment</button>
            <button onClick={() => setShowAddStudent(true)}>+ Add Student</button>
            <button onClick={() => setShowAddTeacher(true)}>+ Add Teacher</button>
            <button onClick={() => setShowAddParent(true)}>+ Add Parent</button>
          </div>
        )}
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
      {showAddStudent && (
        <AddStudent
          onClose={() => setShowAddStudent(false)}
          courseId={id}
        />
      )}
      {showAddTeacher && (
        <AddTeacher
          onClose={() => setShowAddTeacher(false)}
          courseId={id}
        />
      )}
      {showAddParent && (
        <AddParent
          onClose={() => setShowAddParent(false)}
          courseId={id}
        />
      )}
    </Header>
    
  )
  
}
