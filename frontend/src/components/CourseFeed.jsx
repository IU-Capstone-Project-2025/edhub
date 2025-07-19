import React, { useEffect, useState } from "react"
import axios from "axios"
import { useParams, useNavigate } from "react-router-dom"
import "../styles/CourseFeed.css"
import "../styles/LandingPage.css"

export default function CourseFeed() {
  const { id } = useParams()
  const [materials, setMaterials] = useState([])
  const [assignments, setAssignments] = useState([])
  const [assignmentDetails, setAssignmentDetails] = useState({})
  const [materialDetails, setMaterialDetails] = useState({})
  const navigate = useNavigate()

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
            return [ass.post_id, { title: "Loading error", description: "" }]
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
            return [mat.post_id, { title: "Loading error", description: "" }]
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

  useEffect(() => {
    fetchFeed()
  }, [id])

  return (
    <div className="course-feed-root">
      <section className="feed-dual-columns">

        <div className="feed-block materials-block">
          <h2>Materials</h2>
          <div className="vertical-feed">
            {materials.map(mat => (
              <div
                className="vertical-card"
                key={mat.post_id}
                onClick={() => navigate(`/courses/${id}/materials/${mat.post_id}`)}
              >
                <h3>{materialDetails[mat.post_id]?.title}</h3>
                <p>Created: {materialDetails[mat.post_id]?.creation_time}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="feed-block assignments-block">
          <h2>Assignments</h2>
          <div className="vertical-feed">
            {assignments.map(ass => (
              <div
                className="vertical-card"
                key={ass.post_id}
                onClick={() => navigate(`/courses/${id}/assignments/${ass.post_id}`)}
              >
                <h3>{assignmentDetails[ass.post_id]?.title}</h3>
                <p>Created: {assignmentDetails[ass.post_id]?.creation_time}</p>
              </div>
            ))}
          </div>
        </div>

      </section>
    </div>
  )
}
