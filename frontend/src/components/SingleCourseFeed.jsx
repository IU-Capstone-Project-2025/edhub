import React, { useEffect, useState } from "react"
import axios from "axios"
import { useParams, useNavigate } from "react-router-dom"
import "../styles/CourseFeed.css"
import "../styles/LandingPage.css"

export default function SingleCourseFeed() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [posts, setPosts] = useState([])
  const [postDetails, setPostDetails] = useState({})

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
        setPosts(feed)

        const [assignmentDetailResults, materialDetailResults] = await Promise.all([
          Promise.all(
            feed
              .filter(item => item.type === "ass")
              .map(async (ass) => {
                try {
                  const res = await axios.get("/api/get_assignment", {
                    headers: { Authorization: `Bearer ${token}` },
                    params: { assignment_id: ass.post_id, course_id: id },
                  })
                  return [`ass-${ass.post_id}`, res.data]
                } catch {
                  return [`ass-${ass.post_id}`, { title: "Error loading", creation_time: "N/A" }]
                }
              })
          ),
          Promise.all(
            feed
              .filter(item => item.type === "mat")
              .map(async (mat) => {
                try {
                  const res = await axios.get("/api/get_material", {
                    headers: { Authorization: `Bearer ${token}` },
                    params: { material_id: mat.post_id, course_id: id },
                  })
                  return [`mat-${mat.post_id}`, res.data]
                } catch {
                  return [`mat-${mat.post_id}`, { title: "Error loading", creation_time: "N/A" }]
                }
              })
          ),
        ])

        setPostDetails({
          ...Object.fromEntries(assignmentDetailResults),
          ...Object.fromEntries(materialDetailResults),
        })
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
    <div className="course-feed-root">
      <div className="feed-block materials-block">
        <h2>Posts</h2>
        <div className="vertical-feed">
          {posts.length === 0 && (
            <div className="feed-placeholder">No posts yet</div>
          )}
          {posts.map(post => {
            const key = `${post.type}-${post.post_id}`
            const detail = postDetails[key]
            return (
              <div
                key={key}
                className="vertical-card"
                onClick={() =>
                  navigate(
                    post.type === "mat"
                      ? `/courses/${id}/materials/${post.post_id}`
                      : `/courses/${id}/assignments/${post.post_id}`
                  )
                }
              >
                <h3>{detail?.title}</h3>
                <p>Created: {detail?.creation_time}</p>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
