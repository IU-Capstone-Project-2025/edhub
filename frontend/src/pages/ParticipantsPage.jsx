import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import axios from "axios"
import Header from "../components/Header"
import PageMeta from "../components/PageMeta"
import "../styles/ParticipantsPage.css"

export default function ParticipantsPage() {
  const { course_id } = useParams()
  const [teachers, setTeachers] = useState([])
  const [students, setStudents] = useState([])
  const [parentsMap, setParentsMap] = useState({})
  const [role, setRole] = useState(null)
  const [loading, setLoading] = useState(true)

  const isPrivileged = role?.is_teacher || role?.is_admin

  useEffect(() => {
    const fetchAll = async () => {
      const token = localStorage.getItem("access_token")
      const headers = { Authorization: `Bearer ${token}` }
      try {
        const [tRes, sRes, rRes, pRes] = await Promise.all([
          axios.get("/api/get_course_teachers", { headers, params: { course_id } }),
          axios.get("/api/get_enrolled_students", { headers, params: { course_id } }),
          axios.get("/api/get_user_role", { headers, params: { course_id } }),
          axios.get("/api/get_students_parents", { headers, params: { course_id } }),
        ])
        setTeachers(tRes.data)
        setStudents(sRes.data)
        setRole(rRes.data)
        setParentsMap(pRes.data) // { student_email: [{email, name}] }
      } catch (err) {
        alert("Error loading participants: " + (err.response?.data?.detail || err.message))
      } finally {
        setLoading(false)
      }
    }

    fetchAll()
  }, [course_id])

  const removeUser = async (type, email, ownerStudentEmail = null) => {
    if (!window.confirm(`Are you sure you want to remove ${email}?`)) return
    const token = localStorage.getItem("access_token")
    const headers = { Authorization: `Bearer ${token}` }
    const endpoint = type === "student" ? "/api/remove_student" : "/api/remove_parent"

    try {
      await axios.post(endpoint, null, {
        headers,
        params: {
          course_id,
          ...(type === "student" ? { student_email: email } : { parent_email: email }),
        },
      })
      if (type === "student") {
        setStudents((prev) => prev.filter((u) => u.email !== email))
        const newMap = { ...parentsMap }
        delete newMap[email]
        setParentsMap(newMap)
      } else {
        const updated = { ...parentsMap }
        updated[ownerStudentEmail] = updated[ownerStudentEmail].filter(p => p.email !== email)
        setParentsMap(updated)
      }
    } catch (err) {
      alert("Failed to remove: " + (err.response?.data?.detail || err.message))
    }
  }

  if (loading) return <div>Loading participants...</div>

  return (
    <Header>
      <PageMeta title="Course Participants" icon="/edHub_icon.svg" />
      <div className="participants-page">
        <h1>Participants</h1>

        <div className="section">
          <h2>Teachers</h2>
          <div className="user-blocks">
            {teachers.map(t => (
              <div className="user-card" key={t.email}>
                <div>{t.name}</div>
                <div className="email">{t.email}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="section">
          <h2>Students</h2>
          <div className="user-blocks">
            {students.map(s => (
              <div className="user-card" key={s.email}>
                <div>{s.name}</div>
                <div className="email">{s.email}</div>
                {isPrivileged && (
                  <button className="remove-btn" onClick={() => removeUser("student", s.email)}>×</button>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="section">
          <h2>Parents</h2>
          <div className="user-blocks">
            {Object.entries(parentsMap).map(([studentEmail, parentList]) =>
              parentList.map(p => (
                <div className="user-card" key={p.email}>
                  <div>{p.name}</div>
                  <div className="email">{p.email}</div>
                  {isPrivileged && (
                    <button className="remove-btn" onClick={() => removeUser("parent", p.email, studentEmail)}>×</button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </Header>
  )
}
