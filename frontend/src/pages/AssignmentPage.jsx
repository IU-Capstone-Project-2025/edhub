import React, {useEffect, useState ,useRef} from "react"
import "../styles/AssignmentPage.css"
import {useParams} from "react-router-dom"
import axios from "axios"
import AddGrade from "../components/AddGrade"
import PageMeta from "../components/PageMeta"
import StudentAttachment from "../components/StudentAttachment"

export default function AssignmentPage() {
  const { id, post_id } = useParams()
  const [assignmentInfo, setAssignmentInfo] = useState(null)
  const [text,setText] = useState("")
  const [showSubmissionForm, setShowSubmissionForm] = useState(true)
  const [roleData, setRoleData] = useState()
  const [ownEmail, setOwnEmail] = useState("")
  const [mySubmission, setMySubmission] = useState(null)
  const [childrenEmail, setChildrenEmail] = useState(null)
  const [childrenSubmission, setChildrenSubmission] = useState(null)
  const [studentSubmissions, setStudentSubmissions] = useState([])
  const [currentStudentEmail, setCurrentStudentEmail] = useState(null)
  const [showAddGrade, setShowAddGrade] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [studentFileAttachments, setStudentFileAttachments] = useState(null)
  const fileInputRef = useRef(null);

  const onFileChange = (event) =>{
    if(event.target.files[0].size/1000000>5){
        alert("Files should be smaller than 5 MB")
        setSelectedFile(null)
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
    }else{
      setSelectedFile(event.target.files[0])
    }
    
  }
  const fileData = () => {
    if (selectedFile){
      
      return (
				<div>
					<h2>File Details:</h2>
					<p>File Name: {selectedFile.name}</p>
					<p>File Type: {selectedFile.type}</p>
					<p>
						Last Modified: {selectedFile.lastModifiedDate.toDateString()}
					</p>
				</div>
			);
    }
  }


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


  useEffect(() => {
  if (roleData?.is_parent) {
    const fetchChildrenEmail = async () => {
      try {
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/api/get_parents_children", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id }
        })
        setChildrenEmail(res.data)
      } catch (err) {
        alert("Ошибка при загрузке email'а ребёнка: " + (err.response?.data?.detail || err.message))
      }
    }
    fetchChildrenEmail()
  }
}, [roleData, id])


  const fetchMySubmission = async () => {
      try {
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/api/get_submission", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id, assignment_id: post_id , student_email: ownEmail }
        })
        setMySubmission(res.data)
      } catch (err) {
        const msg = err.response?.data?.detail || err.message;
        if (
          msg === "Submission of this user is not found" ||
          (err.response && err.response.status === 404)
        ) {
          setMySubmission(null)
        } else {
          alert("Ошибка при загрузке ответа студента: " + msg)
        }
      }
  }

  useEffect(() => {
    if (roleData?.is_student && ownEmail) {
      fetchMySubmission();
    }
  }, [roleData, ownEmail, id, post_id]);

  const fetchStudentSubmissions = async () => {
      try {
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/api/get_assignment_submissions", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id, assignment_id: post_id  }
        })
        setStudentSubmissions(res.data)

        for(let student of res.data){
          const attachments = await axios.get("/api/get_submission_attachments", {
            headers: { Authorization: `Bearer ${token}` },
            params: { course_id: id, assignment_id: post_id , student_email: student.student_email}
          })
          setStudentFileAttachments([...studentFileAttachments, attachments])
        }
        
      } catch (err) {
          alert("Ошибка при загрузке ответов студентов: " + (err.response?.data?.detail || err.message))
      }
  }

  useEffect(() => {
    if (roleData?.is_teacher || roleData?.is_admin) {
      fetchStudentSubmissions();
    }
  }, [roleData, id, post_id]);

  useEffect(() => {
    if (mySubmission) {
    setShowSubmissionForm(false);
    }
  }, [mySubmission]);
  
  const fetchChildrenSubmission = async () => {
  if (!childrenEmail) return;
  try {
    const token = localStorage.getItem("access_token");
    const submissions = await Promise.all(
      childrenEmail.map(async (child) => {
        if (!child?.email) return null;
        try {
          const res = await axios.get("/api/get_submission", {
            headers: { Authorization: `Bearer ${token}` },
            params: { course_id: id, assignment_id: post_id, student_email: child.email }
          });
          return res.data
        } catch (err) {
          return null;
        }
      })
    );
    setChildrenSubmission(submissions.filter(sub => sub));
  } catch (err) {
    alert("Ошибка при загрузке ответов детей: " + (err.response?.data?.detail || err.message));
  }
}

  useEffect(() => {
    if (roleData?.is_parent && childrenEmail) {
      fetchChildrenSubmission();
    }
  }, [roleData, childrenEmail, id, post_id]);
  
  const handleSubmit = async () => {

    try {
      const token = localStorage.getItem("access_token")
      await axios.post("/api/submit_assignment", null, {
        headers: {Authorization: `Bearer ${token}` },
        params:{course_id: id, assignment_id: post_id, comment: text}
      })
      if (selectedFile) {
      const formData = new FormData();
      formData.append("file", selectedFile, selectedFile.name);

      await axios.post("/api/create_submission_attachment", formData, {
        headers: { Authorization: `Bearer ${token}` },
        params: { course_id: id, assignment_id: post_id, student_email: ownEmail }
      });
    }
      setShowSubmissionForm(false)
      fetchMySubmission()
    } catch (err) {
      alert("Ошибка при отправке ответа: " + (err.response?.data?.detail || err.message))
    }
    
  }


  if (!assignmentInfo) return <div>Loading assignment...</div>
  return (
    <div className="assignment-page">
      <PageMeta title={assignmentInfo.title} icon="/edHub_icon.svg" />
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
              <input type="file" onChange={onFileChange} ref={fileInputRef}/>
              <button 
                className="submit-btn"
                onClick={handleSubmit} 
                disabled={!text.trim()}
              > Submit
              </button>
              {fileData()}
              </div>
            </div>
          )}
          {roleData && roleData.is_student && !showSubmissionForm && mySubmission && (
            <div className="submitted-answer">
              <div className="my-comment-title">Your submission:</div>
              <div className="my-comment">{mySubmission.comment}</div>
              <div>Submitted:{mySubmission.submission_time}</div>
              <div>Last modification time:{mySubmission.last_modification_time}</div>
              {mySubmission.grade && (
                <div className="my-grade">Grade: <b>{mySubmission.grade}</b> (by {mySubmission.gradedby_email})</div>
              )}
            </div>
          )}
          {roleData && roleData.is_parent && Array.isArray(childrenSubmission) && childrenSubmission.length === 0 &&(
            <div className="submitted-answer">Your children haven't submitted anything yet.</div>
          )}
          {roleData && roleData.is_parent && Array.isArray(childrenSubmission) && childrenSubmission.length > 0 && (
            <div>
              {childrenSubmission.map((child, idx) => (
                <div key={idx} className="submitted-answer">
                  <div className="my-comment-title">Your child's {child.student_name || child.student_email || "Child"} submission:</div>
                  <div className="my-comment">{child.comment}</div>
                  <div>Submitted: {child.submission_time}</div>
                  <div>Last modification time: {child.last_modification_time}</div>
                  {child.grade && (
                    <div className="my-grade">Grade: <b>{child.grade}</b> (by {child.gradedby_email})</div>
                  )}
                </div>
              ))}
            </div>
          )}
          {roleData && (roleData.is_teacher || roleData.is_admin) && studentSubmissions && (
            <div className="submitted-answer">
              <div className="my-comment-title">Students' submissions:</div>
              {studentSubmissions.length === 0 && <div>No submissions yet.</div>}
              {studentSubmissions.map((submission, idx) => (
                <div key={idx} className="student-submission-block">
                  <div className="my-comment">
                    <b>{submission.student_name || submission.student_email || "Student"}:</b> {submission.comment}
                  </div>
                  <div>Submitted:{submission.submission_time}</div>
                  <div>Last modification time:{submission.last_modification_time}</div>
                  {submission.grade && (
                    <div className="my-grade">
                      Grade: <b>{submission.grade}</b> {submission.gradedBy && `(by ${submission.gradedBy})`}
                    </div>
                  )}
                  {studentFileAttachments && studentFileAttachments.student_email === submission.student_email &&(
                    <div>{}</div>
                  )}
                  <button 
                    className="grade-btn"
                    onClick={() => {
                      setCurrentStudentEmail(submission.student_email)
                      setShowAddGrade(true)
                    }}>Rate</button>
                  <hr />
                </div>
              ))}
            </div>
)}        
            
        </div>
      </div>
      {showAddGrade && (
        <AddGrade
          onClose={() => setShowAddGrade(false)}
          courseId={id}
          assignmentId={post_id}
          studentEmail={currentStudentEmail}
        />

      )}
    </div>
  )
}