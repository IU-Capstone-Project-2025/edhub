import React, {useEffect, useState } from "react"
import "../styles/AssignmentPage.css"
import {useParams} from "react-router-dom"
import axios from "axios"

export default function AssignmentPage({
  onSubmit,
  onGrade,
  onBack,
}) {
  const { post_id , id: course_id} = useParams()
  const [popup, setPopup] = useState(null)
  const [input, setInput] = useState("")
  const [grade, setGrade] = useState("")
  const [Assignment, setAssignment] = useState()
  const [role, setRole] = useState()
  const [submissions,setSubmissions] = useState([])
  const [mySubmission, setMySubmission] = useState()
  const [studentEmail,setStudentEmail] = useState()

  function onSubmit(comment) {
    try{
      const token = localStorage.getItem("access_token")
      axios.post("/api/submit_assignment", null, {
        headers: { Authorization: `Bearer ${token}` },
        params: { assignment_id: post_id, course_id, comment }
      })
      setInput("")
      setMySubmission({ comment, grade: null, gradedBy: null })
    }catch (err) {
      console.log("Submission error:", err.response?.data);
      alert("Ошибка при отправке задания: " + (
        typeof err.response?.data?.detail === "string"
          ? err.response.data.detail
          : JSON.stringify(err.response?.data?.detail || err.message)
      ))
    }
  }

  function fetchMySubmission() {
    const token = localStorage.getItem("access_token")
    axios.get("/api/get_submission", {
      headers: { Authorization: `Bearer ${token}` },
      params: { assignment_id: post_id, course_id , student_email: studentEmail}
    })
    .then(res => {
      setMySubmission(res.data)
    })
    .catch(err => {
      console.log("My submission fetch error:", err.response?.data);
      alert("Ошибка при загрузке вашего задания: " + (
        typeof err.response?.data?.detail === "string"
          ? err.response.data.detail
          : JSON.stringify(err.response?.data?.detail || err.message)
      ))
    })
  }


  
  useEffect(() => {
    const fetchRole = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const res = await axios.get("/api/get_user_role", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id }
        });
        const data = res.data;
        const user_role = data.is_teacher
          ? "teacher"
          : data.is_student
          ? "student"
          : data.is_parent
          ? "parent"
          : null;
        setRole(user_role);
      } catch (err) {
        setRole(null);
      }
    };
    fetchRole();
}, [course_id]);

    
  

  useEffect (() => {
    const fetchAssignment = async () => {
      try{
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/api/get_assignment", {
          headers:{ Authorization: `Bearer ${token}` },
          params: { assignment_id: post_id , course_id }
        })
        setAssignment(res.data)
      }catch (err) {
        console.log("Assignment fetch error:", err.response?.data);
        alert("Ошибка при загрузке задания: " + (
          typeof err.response?.data?.detail === "string"
            ? err.response.data.detail
            : JSON.stringify(err.response?.data?.detail || err.message)
  ))
}
    }
    fetchAssignment()
  }, [post_id,course_id])

  
  


  // Pop-up for teacher/parent: show submission, grade button
  const handleOpenPopup = (submission) => setPopup(submission)
  const handleClosePopup = () => setPopup(null)
  const handleGrade = () => {
    onGrade && onGrade(popup, grade)
    setGrade("")
    setPopup(null)
  }

  if (!Assignment) {
    return <div>Loading...</div>;
  }

  return (
    <div className="assignment-page">
      <button className="back-btn" onClick={onBack}>← Back to course feed</button>
      <div className="assignment-main">
        <div className="assignment-left">
          <h1>{Assignment.title}</h1>
          <h1>my role:{role}</h1>
          <p>{Assignment.description}</p>
          <p>Created by: {Assignment.author}</p>
          <p>Assignment ID : {Assignment.assignment_id}</p>
          <p>Created : {Assignment.creation_time}</p>
        </div>
        <div className="assignment-right">
          {role === "teacher" && (
            <>
              <h2>Student Submissions</h2>
              <div className="submission-list">
                {submissions.length === 0 && <div className="empty">No submissions yet.</div>}
                {submissions.map((s, i) => (
                  <div key={i} className="submission-card" onClick={() => handleOpenPopup(s)}>
                    <div>{s.studentName}</div>
                    <div className="submission-status">
                      {s.grade ? <>Graded: <b>{s.grade}</b></> : <span>Not graded</span>}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {role === "parent" && (
            <>
              <h2>Your Children's Submissions</h2>
              <div className="submission-list">
                {submissions.length === 0 && <div className="empty">No submissions yet.</div>}
                {submissions.map((s, i) => (
                  <div key={i} className="submission-card" onClick={() => handleOpenPopup(s)}>
                    <div>{s.studentName}</div>
                    <div className="submission-status">
                      {s.grade ? <>Graded: <b>{s.grade}</b></> : <span>Not graded</span>}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {role === "student" && (
            <div className="student-submit-block">
              {!mySubmission ? (
                <>
                  <textarea
                    placeholder="Type your answer here..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                  />
                  <button
                    className="submit-btn"
                    disabled={!input.trim()}
                    onClick={() => { onSubmit && onSubmit(input); setInput(""); }}
                  >Submit</button>
                </>
              ) : (
                <div className="submitted-answer">
                  <div className="my-comment-title">Your submission:</div>
                  <div className="my-comment">{mySubmission.comment}</div>
                  {mySubmission.grade && (
                    <div className="my-grade">Grade: <b>{mySubmission.grade}</b> (by {mySubmission.gradedBy})</div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {popup && (
        <div className="popup-bg" onClick={handleClosePopup}>
          <div className="popup-card" onClick={e => e.stopPropagation()}>
            <div className="popup-title">{popup.studentName}'s Submission</div>
            <div className="popup-content">{popup.comment}</div>
            {role === "teacher" && (
              <div className="popup-grade-block">
                <input
                  type="text"
                  placeholder="Grade"
                  value={grade}
                  onChange={e => setGrade(e.target.value)}
                />
                <button className="grade-btn" onClick={handleGrade}>Set grade</button>
              </div>
            )}
            {popup.grade && (
              <div className="popup-graded">Grade: <b>{popup.grade}</b> {popup.gradedBy && `(by ${popup.gradedBy})`}</div>
            )}
            <button className="close-btn" onClick={handleClosePopup}>Close</button>
          </div>
        </div>
      )}
    </div>
  )
}
