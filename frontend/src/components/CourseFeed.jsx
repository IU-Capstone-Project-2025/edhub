import React, { useEffect, useState } from "react"
import axios from "axios"
import { useParams, useNavigate } from "react-router-dom"
import "../styles/CourseFeed.css"

export default function CourseFeed() {
  const { id } = useParams()
  const [materials, setMaterials] = useState([])
  const [assignments, setAssignments] = useState([])
  const [assignmentDetails, setAssignmentDetails] = useState({})
  const [materialDetails, setMaterialDetails] = useState({})
  const navigate = useNavigate()

  useEffect(() => {
    const fetchFeed = async () => {
      const token = localStorage.getItem("access_token")
      if (!token) {
        window.location.href = "/auth"
        return
      }

      try {
        const res = await axios.get("/api/get_course_feed", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id },
        })
        const feed = res.data
        const matList = feed.filter(item => item.type === "mat")
        const assList = feed.filter(item => item.type === "ass")
        setMaterials(matList)
        setAssignments(assList)

        const [assignmentDetailResults, materialDetailResults] = await Promise.all([
          Promise.all(assList.map(async (ass) => {
            try {
              const res = await axios.get("/api/get_assignment", {
                headers: { Authorization: `Bearer ${token}` },
                params: { assignment_id: ass.post_id, course_id: id },
              })
              return [ass.post_id, res.data]
            } catch {
              return [ass.post_id, { title: "Ошибка загрузки", description: "" }]
            }
          })),
          Promise.all(matList.map(async (mat) => {
            try {
              const res = await axios.get("/api/get_material", {
                headers: { Authorization: `Bearer ${token}` },
                params: { material_id: mat.post_id, course_id: id },
              })
              return [mat.post_id, res.data]
            } catch {
              return [mat.post_id, { title: "Ошибка загрузки", description: "" }]
            }
          })),
        ])

        setAssignmentDetails(Object.fromEntries(assignmentDetailResults))
        setMaterialDetails(Object.fromEntries(materialDetailResults))

      } catch (err) {
        console.error("Error fetching feed:", err)
        if (err.response?.status === 401) {
          localStorage.removeItem("access_token")
          window.location.href = "/auth"
        }
      }
    }

    fetchFeed()
  }, [id])

  return (
    <div className="course-feed-columns">
      <div className="feed-column">
        <h2>Materials</h2>
        <div className="feed-list">
          {materials.length === 0 && <div className="feed-placeholder">No materials yet</div>}
          {materials.map(mat => (
            <div
              className="feed-card"
              key={mat.post_id}
              onClick={() => navigate(`/courses/${id}/materials/${mat.post_id}`)}
            >
              <p>{materialDetails[mat.post_id]?.title}</p>
              <p>Material ID: {materialDetails[mat.post_id]?.material_id}</p>
              <p>Creation Date: {materialDetails[mat.post_id]?.creation_time}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="feed-column">
        <h2>Assignments</h2>
        <div className="feed-list">
          {assignments.length === 0 && <div className="feed-placeholder">No assignments yet</div>}
          {assignments.map(ass => (
            <div
              className="feed-card"
              key={ass.post_id}
              onClick={() => navigate(`/courses/${id}/assignments/${ass.post_id}`)}
            >
              <p>{assignmentDetails[ass.post_id]?.title}</p>
              <p>Assignment ID: {assignmentDetails[ass.post_id]?.assignment_id}</p>
              <p>Creation Date: {assignmentDetails[ass.post_id]?.creation_time}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
