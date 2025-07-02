import React, {useEffect, useState } from "react"
import "../styles/AssignmentPage.css"
import {useParams} from "react-router-dom"
import axios from "axios"

export default function AssignmentPage() {
  const { id, post_id } = useParams()
  const [assignmentInfo, setAssignmentInfo] = useState(null)

  
  useEffect(() => {
    const fetchAssignmentInfo = async () => {
      try{
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/api/get_assignment", {
          headers: { Authorization: `Bearer ${token}` },
          params: { assignment_id:post_id, course_id: id }
        })
        setAssignmentInfo(res.data)
        
      }catch(err){
        alert("Ошибка при загрузке курса: " + (err.response?.data?.detail || err.message))
      }
    }
    fetchAssignmentInfo()
  }, [id])

  return (
    <div className="assignment-page">
      <a href="../">
        <button className="back-btn">← Back to course feed</button>
      </a>
      <div className="assignment-main">
        <div className="assignment-left">
          <h1>{assignmentInfo.title}</h1>
          <p>{assignmentInfo.description}</p>
          <p>Assignment ID : {assignmentInfo.material_id}</p>
          <p>Created : {assignmentInfo.creation_time}</p>
          <p>author : {assignmentInfo.author}</p>
        </div>
        <div className="assignment-right">
          <h2>Submissions</h2>
        </div>
      </div>

    </div>
  )
}