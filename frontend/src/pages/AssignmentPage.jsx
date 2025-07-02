import React, {useEffect, useState } from "react"
import "../styles/AssignmentPage.css"
import {useParams} from "react-router-dom"
import axios from "axios"

export default function AssignmentPage() {
  const { id, post_id } = useParams()
  const [assignmentInfo, setAssignmentInfo] = useState(null)
  const [text,setText] = useState("")
  const [showSubmissionForm, setShowSubmissionForm] = useState(true)
  const [roleData, setRoleData] = useState()
  const [ownEmail, setOwnEmail] = useState("")
  const [mySubmission, setMySubmission] = useState(null)



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

    const fetchRoleData = async () => {
      try{
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/api/get_user_role", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id },
        })
        setRoleData(res.data)
      }catch(err){
        alert("Ошибка при загрузке роли пользователя: " + (err.response?.data?.detail || err.message))
      }
    }
    fetchRoleData()

    const fetchEmail = async () => {
      try {
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/api/get_user_info", {
          headers: { Authorization: `Bearer ${token}` },
        })
        setOwnEmail(res.data.email)
      } catch (err) {
        alert("Ошибка при загрузке email'а пользователя: " + (err.response?.data?.detail || err.message))
      }
    }
    fetchEmail()

    
  }, [id])
  const fetchMySubmission = async () => {
      try {
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/api/get_submission", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id, assignment_id: post_id , student_email: ownEmail }
        })
        setMySubmission(res.data)
      } catch (err) {
        alert("Ошибка при загрузке ответа студента: " + (err.response?.data?.detail || err.message))
      }
  }
  useEffect(() => {
    if (roleData?.is_student && ownEmail) {
      fetchMySubmission();
    }
  }, [roleData, ownEmail, id, post_id]);

  useEffect(() => {
    if (mySubmission) {
    setShowSubmissionForm(false);
    }
  }, [mySubmission]);

  const handleSubmit = async () => {
    // if (!studentEmail.trim()) {
    //   alert("Student's Email is required")
    //   return
    // }

    try {
      const token = localStorage.getItem("access_token")
      await axios.post("/api/submit_assignment", null, {
        headers: {Authorization: `Bearer ${token}` },
        params:{course_id: id, assignment_id: post_id, comment: text}
      })
      setShowSubmissionForm(false)
      fetchMySubmission()
    } catch (err) {
      alert("Ошибка при отправке ответа: " + (err.response?.data?.detail || err.message))
    }
    
  }

  if (!assignmentInfo) return <div>Loading assignment...</div>
  return (
    <div className="assignment-page">
      <a href="../">
        <button className="back-btn">← Back to course feed</button>
      </a>
      <div className="assignment-main">
        <div className="assignment-left">
          <h1>{assignmentInfo.title}</h1>
          <p>{assignmentInfo.description}</p>
          <p>Assignment ID : {assignmentInfo.assignment_id}</p>
          <p>Created : {assignmentInfo.creation_time}</p>
          <p>Current Email: {ownEmail}</p>
          <p>author : {assignmentInfo.author}</p>
        </div>
        <div className="assignment-right">
          {roleData && roleData.is_student && showSubmissionForm && !mySubmission &&(
            <div className="student-submit-block">
              <h2>Submit your work</h2>
              <div>
              <textarea 
                placeholder="Write your submission here..."
                value={text} onChange={(e) => setText(e.target.value)}
                rows="10" 
                cols="30"/>
              <button 
                className="submit-btn"
                onClick={handleSubmit} 
                disabled={!text.trim()}
              > Submit
              </button>
              </div>
            </div>
          )}
          {roleData && roleData.is_student && !showSubmissionForm && mySubmission && (
            <div className="submitted-answer">
              <div className="my-comment-title">Your submission:</div>
              <div className="my-comment">{mySubmission.comment}</div>
              {mySubmission.grade && (
                <div className="my-grade">Grade: <b>{mySubmission.grade}</b> (by {mySubmission.gradedBy})</div>
              )}
            </div>
          )}
          
        </div>
      </div>

    </div>
  )
}