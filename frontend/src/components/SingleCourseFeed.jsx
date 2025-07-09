import React, { useEffect, useState } from "react"
import axios from "axios"
import { useParams, useNavigate } from "react-router-dom"
import "../styles/SingleCourseFeed.css"

export default function SingleCourseFeed() {
  const { id } = useParams()
  const [materials, setMaterials] = useState([])
  const [assignments, setAssignments] = useState([])
  const [assignmentDetails, setAssignmentDetails] = useState({})
  const [materialDetails, setMaterialDetails] = useState({})
  const [commonQueue,setCommonQueue] = useState([])
  const [commonQueueDetails,setCommonQueueDetails] = useState([])
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
        setCommonQueue(feed)
        commonQueue.sort(function(a,b){return a.timeadded-b.timeadded})
        const [assignmentDetailResults, materialDetailResults] = await Promise.all([
          Promise.all(assList.map(async (ass) => {
            try {
              const res = await axios.get("/api/get_assignment", {
                headers: { Authorization: `Bearer ${token}` },
                params: { assignment_id: ass.post_id, course_id: id },
              })
              return [`ass-${ass.post_id}`, res.data]
            } catch {
              return [`ass-${ass.post_id}`, { title: "Ошибка загрузки", description: "" }]
            }
          })),
          Promise.all(matList.map(async (mat) => {
            try {
              const res = await axios.get("/api/get_material", {
                headers: { Authorization: `Bearer ${token}` },
                params: { material_id: mat.post_id, course_id: id },
              })
              return [`mat-${mat.post_id}`, res.data]
            } catch {
              return [`mat-${mat.post_id}`, { title: "Ошибка загрузки", description: "" }]
            }
          })),
        ])

        setAssignmentDetails(Object.fromEntries(assignmentDetailResults))
        setMaterialDetails(Object.fromEntries(materialDetailResults))
        const allDetails = { ...Object.fromEntries(assignmentDetailResults),
           ...Object.fromEntries(materialDetailResults) }
        setCommonQueueDetails(allDetails)
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
        <h2>Posts</h2>
        <div className="feed-list">
          {commonQueue.length === 0 && <div className="feed-placeholder">No posts yet</div>}
          {commonQueue.map(post => (
            <div
              className="feed-card"
              onClick={() => {if(post.type==="mat"){
                navigate(`/courses/${id}/materials/${post.post_id}`)
            }else{
                navigate(`/courses/${id}/assignments/${post.post_id}`)
            }}}
            >
              <p>Title: {commonQueueDetails[`${post.type}-${post.post_id}`]?.title}</p>
              <p>Post ID: {post.post_id}</p>
              <p>Post type: {post.type}</p>
              <p>Creation Date: {post.timeadded}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
