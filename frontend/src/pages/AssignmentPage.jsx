import React, {useEffect, useState, useRef} from "react"
import "../styles/AssignmentPage.css"
import {useParams, useNavigate} from "react-router-dom"
import axios from "axios"
import AddGrade from "../components/AddGrade"
import PageMeta from "../components/PageMeta"

function formatText(text) {
  if (!text) return "";
  let html = text
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>') // bold: **text**
    .replace(/__(.*?)__/g, '<u>$1</u>') // underline: __text__
    .replace(/\*(.*?)\*/g, '<i>$1</i>'); // italic: *text*
  return html;
}

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
  const navigate = useNavigate();
  const [showAddGrade, setShowAddGrade] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null);
  const [myAttachment,setMyAttachment] = useState([])
  const [childrenAttachment, setChildrenAttachment] = useState([])
  const [assignmentAttachments, setAssignmentAttachments] = useState([])

  const onFileChange = (event) =>{
    if(event.target.files[0]?.size/1000000>5){
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
        alert("Error loading assignment: " + (err.response?.data?.detail || err.message))
        console.log("Error loading assignment: " + (err.response?.data?.detail || err.message));
        navigate("/courses/" + id);
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
        alert("Error while user downloading: " + (err.response?.data?.detail || err.message))
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
        alert("Error while user' email downloading: " + (err.response?.data?.detail || err.message))
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
        alert("Error while children' mail downloading: " + (err.response?.data?.detail || err.message))
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
          alert("Error while student' task downloading: " + msg)
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
      } catch (err) {
          alert("Error while students' answers downloading: " + (err.response?.data?.detail || err.message))
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
    alert("Error loading student answers: " + (err.response?.data?.detail || err.message));
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
      alert("Error submitting answer: " + (err.response?.data?.detail || err.message))
    }
    
  }

  const fetchChildrenSubmissionAttachment = async()=> {
    if (!childrenEmail) return
    try{
      const token = localStorage.getItem("access_token")
      const attachments = await Promise.all(
        childrenEmail.map(async(child)=>{
          if(!child?.email) return null;
          try{
            const res = await axios.get("/api/get_submission_attachments", {
              headers: { Authorization: `Bearer ${token}` },
              params: { course_id: id, assignment_id: post_id, student_email:child.email },
            });
            return res.data
          }catch(err){
            return null;
          }
        })
      )
      setChildrenAttachment(attachments.filter(sub=>sub))
    }catch(err){
      alert("failure to fetch submission attachment")
      setMyAttachment([])
    }
  }
  useEffect(() => {
    if (roleData?.is_parent && childrenEmail) {
      fetchChildrenSubmissionAttachment();
    }
  }, [roleData, childrenEmail, id, post_id]);

  const fetchMySubmissionAttachment = async(student_email)=> {
    try{
      const token = localStorage.getItem("access_token")
      const res = await axios.get("/api/get_submission_attachments", {
        headers: { Authorization: `Bearer ${token}` },
        params: { course_id: id, assignment_id: post_id, student_email },
      });
      setMyAttachment(res.data || [])
    }catch(err){
      alert("failure to fetch submission attachment")
      setMyAttachment([])
    }
  }
  useEffect(() => {
    if (mySubmission && roleData && roleData.is_student) {
      fetchMySubmissionAttachment(mySubmission.student_email);
    }
  }, [mySubmission,roleData]);
  const downloadAttachment = async (file_id,student_email) => {
    try {
      const token = localStorage.getItem("access_token");

      const response = await axios.get("/api/download_submission_attachment", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        params: {
          course_id: id,
          assignment_id: post_id,
          student_email,
          file_id,
        },
        responseType: "blob",
      });

      const contentDisposition = response.headers["content-disposition"];
      const filenameMatch = contentDisposition?.match(/filename="?([^"]+)"?/);
      const filename = filenameMatch ? filenameMatch[1] : "downloaded_file";

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();

      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Error downloading attachment: " + (err.response?.data?.detail || err.message));
    }
  };

  //Assignment attachment block
  const uploadAssignmentAttachment = async()=>{
      try{
        const token = localStorage.getItem("access_token")
        if (selectedFile){
          const formData = new FormData();
          formData.append("file", selectedFile, selectedFile.name);
          await axios.post("/api/create_assignment_attachment", formData, {
            headers: { Authorization: `Bearer ${token}` },
            params:{ course_id: id, assignment_id: post_id}
          })
        }
        fetchAssignmentAttachments();
      }catch(err){
        alert("Error uploading assignment attachment: " + (err.response?.data?.detail || err.message))
      }
    }
  
    const fetchAssignmentAttachments = async () => {
      try{
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/api/get_assignment_attachments", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id, assignment_id: post_id }
        })
        setAssignmentAttachments(res.data || [])
      }catch(err){
        alert("Error fetching assignment attachment: " + (err.response?.data?.detail || err.message))
        setAssignmentAttachments([]);
      }
    }
    
    useEffect(() => {
      if (assignmentInfo) {
        fetchAssignmentAttachments();
      }
    }, [assignmentInfo]);
  
    const downloadAssignmentAttachment = async (file_id) => {
      try {
        const token = localStorage.getItem("access_token");
    
        const response = await axios.get("/api/download_assignment_attachment", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          params: {
            course_id: id,
            assignment_id: post_id,
            file_id,
          },
          responseType: "blob",
        });
    
        const contentDisposition = response.headers["content-disposition"];
        const filenameMatch = contentDisposition?.match(/filename="?([^"]+)"?/);
        const filename = filenameMatch ? filenameMatch[1] : "downloaded_file";
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        alert("Error downloading assignment attachment: " + (err.response?.data?.detail || err.message));
      }
    };

  if (!assignmentInfo) return <div>Loading assignment...</div>
  return (
    <div className="assignment-page">
      <PageMeta title={assignmentInfo.title} icon="/edHub_icon.svg" />
      <a href="../">
        <button className="back-btn">← Back to course feed</button>
      </a>
      <div className="assignment-main">
        <div className="assignment-left">
          <div className="assignment-date">{assignmentInfo.creation_time}</div>
          <h1 className="assignment-title">{assignmentInfo.title}</h1>
          {roleData && (roleData.is_teacher || roleData.is_admin) && (
            <div
              className="remove-assignment-text"
              onClick={async () => {
                if (window.confirm("Are you sure you want to remove this assignment? This action cannot be undone.")) {
                  try {
                    const token = localStorage.getItem("access_token")
                    await axios.post("/api/remove_assignment", null, {
                      headers: { Authorization: `Bearer ${token}` },
                      params: { course_id: id, assignment_id: post_id }
                    })
                    window.location.assign("../")
                  } catch (err) {
                    alert("Error deleting assignment: " + (err.response?.data?.detail || err.message))
                  }
                }
              }}
            >
              Delete assignment
            </div>
          )}
          <p className="assignment-desc" dangerouslySetInnerHTML={{__html: formatText(assignmentInfo.description)}} />
          <div className="my-comment assignment-desc">
            <span style={{ fontWeight: 'bold', marginRight: 8 }}>Attachments</span><br />
            {assignmentAttachments?.length ===0 ? (
              <span>No attachments uploaded yet.</span>
            ) : (
              <ul className="submission-list">
                {assignmentAttachments?.map((attachment) => (
                  <li key={attachment.file_id}>
                    <button
                      className="link-style-button"
                      onClick={() => downloadAssignmentAttachment(attachment.file_id)}
                    >
                      {attachment.filename}
                    </button>
                  </li>
                ))}
              </ul>
            )}
            {assignmentInfo && roleData && roleData?.is_teacher && assignmentAttachments.length ===0 &&(
              <div className="student-submit-block">
                <h2>Upload Attachment</h2>
                <div>
                <div className="submission-buttons-row">
                  <label htmlFor="file-upload" className="file-input">
                    Choose File
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    onChange={onFileChange}
                  />
                  <button 
                    className="submit-btn"
                    onClick={uploadAssignmentAttachment}
                  >
                    Upload
                  </button>
                </div>
                {fileData() && (
                  <div className="file-details">
                    {fileData()}
                  </div>
                )}
                </div>
            </div>
            )}

          </div>
        </div>
        <div className="assignment-right">
          {roleData && !roleData.is_admin && roleData.is_student && showSubmissionForm && !mySubmission &&(
            <div className="student-submit-block">
              <h2>Submit your work</h2>
              <div>
              <textarea 
                placeholder="Write your submission here..."
                value={text} onChange={(e) => setText(e.target.value)}
                rows="10" 
                cols="30"/>
              <div className="submission-buttons-row">
                <label htmlFor="file-upload" className="file-input">
                  Choose File
                </label>
                <input
                  id="file-upload"
                  type="file"
                  ref={fileInputRef}
                  style={{ display: 'none' }}
                  onChange={onFileChange}
                />
                <button 
                  className="submit-btn"
                  onClick={handleSubmit} 
                  disabled={!text.trim()}
                >
                  Submit
                </button>
              </div>
              {fileData() && (
                <div className="file-details">
                  {fileData()}
                </div>
              )}
              </div>
            </div>
          )}
          {roleData && !roleData.is_admin && roleData.is_student && !showSubmissionForm && mySubmission && (
            <div className="submitted-answer">
              <div className="my-comment-title">Your answer:</div>
              <div className="my-comment assignment-desc" dangerouslySetInnerHTML={{__html: formatText(mySubmission.comment)}} />
              <div className="assignment-date">{mySubmission.submission_time}</div>
              {mySubmission.grade && (
                <div className="my-grade">Grade: <b>{mySubmission.grade}</b> <span className="grade-by">({mySubmission.gradedby_email})</span></div>
              )}
              {roleData && mySubmission && myAttachment && myAttachment.length !== 0 && !roleData.is_admin && roleData.is_student && (
                <button 
                  className="link-style-button"
                  onClick={()=>{ downloadAttachment(myAttachment[0].file_id, mySubmission.student_email)}}
                >
                  {myAttachment[0].filename}
                </button>
              )}
            </div>
          )}
          {roleData && !roleData.is_admin && roleData.is_parent && Array.isArray(childrenSubmission) && childrenSubmission.length === 0 &&(
            <div className="submitted-answer">Your children haven't submitted anything yet.</div>
          )}
          {roleData && !roleData.is_admin && roleData.is_parent && Array.isArray(childrenSubmission) && childrenSubmission.length > 0 && (
            <div className="parent-submissions">
              {childrenSubmission.map((child, idx) => (
                <div key={idx} className="submitted-answer">
                  <div className="my-comment-title">Child's answer: {child.student_name || child.student_email || "Child"}</div>
                  <div className="my-comment assignment-desc" dangerouslySetInnerHTML={{__html: formatText(child.comment)}} />
                  <div className="assignment-date">{child.submission_time}</div>
                  {child.grade && (
                  <div className="my-grade">Grade: <b>{child.grade}</b> <span className="grade-by">({child.gradedby_email})</span></div>
                  )}
                  {childrenAttachment &&childrenAttachment.length>0 && (
                    <button
                      className="link-style-button"
                      onClick={()=>{downloadAttachment(childrenAttachment[idx][0].file_id,childrenAttachment[idx][0].student_email)}}
                    >
                      {childrenAttachment[idx][0].filename}
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
          {roleData && roleData.is_teacher && studentSubmissions && (
            <div className="teacher-submissions">
              <div className="my-comment-title" style={{marginBottom: 24}}>Student answers:</div>
              {studentSubmissions.length === 0 && <div className="empty">No answers yet.</div>}
              <div className="teacher-submissions-list">
                {studentSubmissions.map((submission, idx) => (
                  <div
                    key={idx}
                    className="student-submission-block clickable-submission"
                    onClick={() => navigate(`/courses/${id}/assignments/${post_id}/submission/${submission.student_email}`)}
                    style={{cursor: "pointer"}}
                  >
                    <div className="my-comment assignment-desc">
                      <b>{submission.student_name || submission.student_email || "Student"}:</b> <span dangerouslySetInnerHTML={{__html: formatText(submission.comment)}} />
                    </div>
                    <div className="assignment-date">{submission.submission_time}</div>
                    {submission.grade && (
                      <div className="my-grade">
                        Grade: <b>{submission.grade}</b> {submission.gradedBy && <span className="grade-by">({submission.gradedBy})</span>}
                      </div>
                    )}
                    <button 
                      className="grade-btn"
                      onClick={e => {
                        e.stopPropagation();
                        setCurrentStudentEmail(submission.student_email)
                        setShowAddGrade(true)
                      }}>Grade</button>
                  </div>
                ))}
              </div>
            </div>
          )}
            
        </div>
      </div>
      {showAddGrade && (
        <AddGrade
          onClose={() => {
              setShowAddGrade(false);
              fetchStudentSubmissions();
            }}          
          courseId={id}
          assignmentId={post_id}
          studentEmail={currentStudentEmail}
        />

      )}
    </div>
  )
}
