import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import axios from "axios"
import Header from "../components/Header"
import PageMeta from "../components/PageMeta"
import CourseTabs from "../components/CoursesTabs"
import "../styles/LandingPage.css"
import "../styles/ParticipantsPage.css"

export default function ParticipantsPage() {
  const { id: course_id } = useParams()
  const [students, setStudents] = useState([])
  const [parentsMap, setParentsMap] = useState({})
  const [role, setRole] = useState(null)
  const [loading, setLoading] = useState(true)
  const [courseInfo, setCourseInfo] = useState(null)
  const isPrivileged = role?.is_teacher || role?.is_admin
  const [deletedStudents, setDeletedStudents] = useState([])
  const [activeView, setActiveView] = useState("students")

  useEffect(() => {
    const fetchAll = async () => {
      const token = localStorage.getItem("access_token")
      const headers = { Authorization: `Bearer ${token}` }
      try {
        const [cRes, sRes, rRes] = await Promise.all([
          axios.get("/api/get_course_info", { headers, params: { course_id } }),
          axios.get("/api/get_enrolled_students", { headers, params: { course_id } }),
          axios.get("/api/get_user_role", { headers, params: { course_id } }),
        ])
        setCourseInfo(cRes.data)
        setStudents(sRes.data)
        setRole(rRes.data)

        const parentsMapResult = {}
        await Promise.all(sRes.data.map(async (student) => {
          try {
            const pres = await axios.get("/api/get_students_parents", { headers, params: { course_id, student_email: student.email } })
            parentsMapResult[student.email] = pres.data
          } catch (err) {
            parentsMapResult[student.email] = []
          }
        }))
        setParentsMap(parentsMapResult)
      } catch (err) {
        alert("Error loading participants: " + (err.response?.data?.detail || err.message))
      } finally {
        setLoading(false)
      }
    }

    fetchAll()
  }, [course_id])

  const [teachers, setTeachers] = useState([]);
useEffect(() => {
  if (isPrivileged) {
    const fetchTeachers = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const headers = { Authorization: `Bearer ${token}` };
        const res = await axios.get("/api/get_course_teachers", {
          headers,
          params: { course_id },
        });
        setTeachers(res.data);
      } catch (err) {
        alert("Failed to fetch teachers");
      }
    };
    fetchTeachers();
  }
}, [course_id, isPrivileged]);


  const removeUser = async (type, email, ownerStudentEmail = null) => {
  if (!window.confirm(`Are you sure you want to remove ${email}?`)) return

  const token = localStorage.getItem("access_token")
  const headers = { Authorization: `Bearer ${token}` }

  if (type === "teacher") {
    try {
      await axios.post("/api/remove_teacher", null, {
        headers,
        params: {
          course_id,
          removing_teacher_email: email,
        },
      })
      setTeachers((prev) => prev.filter((t) => t.email !== email))
    } catch (err) {
      alert("Failed to remove teacher: " + (err.response?.data?.detail || err.message))
    }
    return
  }

  const endpoint = type === "student" ? "/api/remove_student" : "/api/remove_parent"

  try {
    await axios.post(endpoint, null, {
      headers,
      params: {
        course_id,
        ...(type === "student"
          ? { student_email: email }
          : { parent_email: email, student_email: ownerStudentEmail }),
      },
    })
    if (type === "student") {
      setStudents((prev) => prev.filter((u) => u.email !== email))
      setDeletedStudents((prev) => [...prev, email])
    } else {
      const updated = { ...parentsMap }
      updated[ownerStudentEmail] = updated[ownerStudentEmail].filter((p) => p.email !== email)
      setParentsMap(updated)
    }
  } catch (err) {
    alert("Failed to remove: " + (err.response?.data?.detail || err.message))
  }
}

  if (loading || !courseInfo) return <div className="landing-content">Loading participants...</div>

  return (
    <Header>
      <PageMeta title={courseInfo.title} icon="/edHub_icon.svg" />
      <div className="course-page">
        <div className="course-page-header">
          <h1 className="course-title">{courseInfo.title}</h1>
          <CourseTabs
          
            activeTab="Participants"
            onTabChange={(tab) => {
              if (tab === "Course") {
                window.location.href = `/courses/${course_id}`;
              } else if (tab === "Participants") {
                window.location.href = `/courses/${course_id}/participants`;
              } else if (tab === "Grades") {
                window.location.href = `/courses/${course_id}/grades`;
              }
            }}
            availableTabs={["Course", "Participants", "Grades"]}
          />
        </div>
        {isPrivileged && (
  <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px", marginBottom: "12px" }}>
    <div className={`part-button green ${activeView === "students" ? "active" : ""}`} onClick={() => setActiveView("students")}>
      Students & Parents
    </div>
    <div className={`part-button green ${activeView === "teachers" ? "active" : ""}`} onClick={() => setActiveView("teachers")}>
      Teachers
    </div>
  </div>
)}
{activeView === "students" ? (
  <div className="participants-wrapper">
    <div className="participants-labels">
      <div className="label-left">Students</div>
      <div className="label-right">Parents</div>
    </div>
    {students.map((s) => (
      <div key={s.email} className="participant-row">
        <div className="participant-left">
          <div className="participant-card">
            <div style={{ fontWeight: 600 }}>{s.name}</div>
            <div className="email">{s.email}</div>
            {isPrivileged && (
              <button onClick={() => removeUser("student", s.email)} className="remove-btn">×</button>
            )}
          </div>
        </div>

        <div className="participant-right">
          {deletedStudents.includes(s.email) ? (
            <div className="participant-card no-parent-text">Student was removed</div>
          ) : (
            parentsMap[s.email]?.length > 0 ? (
              parentsMap[s.email].map((p) => (
                <div key={p.email} className="participant-card">
                  <div style={{ fontWeight: 600 }}>{p.name}</div>
                  <div className="email">{p.email}</div>
                  {isPrivileged && (
                    <button
                      onClick={() => removeUser("parent", p.email, s.email)}
                      className="remove-btn"
                    >
                      ×
                    </button>
                  )}
                </div>
              ))
            ) : (
              <div className="participant-card no-parent-text">No parents added</div>
            )
          )}
        </div>    
    </div>
    ))}
  </div>
) : (
  <div className="participants-wrapper">
    <div className="participants-labels">
      <div className="label-left">Teachers</div>
      <div className="label-right"></div>
    </div>
    {teachers.map((t) => (
  <div key={t.email} className="participant-row" style={{ width: "100%" }}>
    <div className="participant-single">
      <div className="participant-card">
        <div style={{ fontWeight: 600 }}>{t.name}</div>
        <div className="email">{t.email}</div>
        {isPrivileged && t.email !== role?.email && (
          <button
            onClick={() => removeUser("teacher", t.email)}
            className="remove-btn"
          >
            ×
          </button>
        )}
      </div>
    </div>
  </div>
))}

  </div>
)}
</div>
    </Header>
  )
}
