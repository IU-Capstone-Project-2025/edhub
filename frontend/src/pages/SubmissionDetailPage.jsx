
import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import "../styles/AssignmentPage.css";

function formatText(text) {
  if (!text) return "";
  let html = text
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
    .replace(/__(.*?)__/g, '<u>$1</u>')
    .replace(/\*(.*?)\*/g, '<i>$1</i>');
  return html;
}

export default function SubmissionDetailPage() {
  const navigate = useNavigate();
  const { id, post_id, student_email } = useParams();
  const [submission, setSubmission] = useState(null);
  const [grade, setGrade] = useState("");
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [attachments, setAttachments] = useState([]);

  const fetchSubmission = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await axios.get("/api/get_submission", {
        headers: { Authorization: `Bearer ${token}` },
        params: { course_id: id, assignment_id: post_id, student_email },
      });
      // Patch: ensure submission_time is present and fallback to other possible fields
      let sub = res.data;
      if (sub && !sub.submission_time && sub.submissionTime) {
        sub.submission_time = sub.submissionTime;
      }
      setSubmission(sub);
    } catch (err) {
      alert("Error loading submission: " + (err.response?.data?.detail || err.message))
      console.log("Error loading submission: " + (err.response?.data?.detail || err.message));
      navigate("/courses/" + id + "/assignments/"+ post_id);
    }
  };
  useEffect(() => {
    fetchSubmission();
  }, [id, post_id, student_email]);

  const handleGradeSubmit = async () => {
    if (!grade.trim()) {
      alert("Grade field cannot be empty");
      return;
    }
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      await axios.post("/api/grade_submission", null, {
        headers: { Authorization: `Bearer ${token}` },
        params: {
          student_email,
          course_id: id,
          assignment_id: post_id,
          grade,
        },
      });
      setSuccess(true);
      setLoading(false);
      setTimeout(() => {
        fetchSubmission();
      }, 500);
    } catch (err) {
      setLoading(false);
      alert("Error while adding grade: " + (err.response?.data?.detail || err.message));
    }
  };

  const fetchSubmissionAttachments = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await axios.get("/api/get_submission_attachments", {
        headers: { Authorization: `Bearer ${token}` },
        params: { course_id: id, assignment_id: post_id, student_email },
      });
      setAttachments(res.data || []);
    } catch (err) {
      alert("Error fetching attachments: " + (err.response?.data?.detail || err.message));
      setAttachments([]);
    }
  }
  useEffect(() => {
    if (submission) {
      fetchSubmissionAttachments();
    }
  }, [submission]);

const downloadAttachment = async (file_id) => {
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

  
  if (submission === null) {
    return (
      <div className="assignment-page">
        <button className="back-btn" onClick={() => navigate(-1)}>
          ← Back to submissions
        </button>
        <div className="assignment-main">
          <div className="assignment-left">
            <h1 className="assignment-title">Loading submission...</h1>
          </div>
        </div>
      </div>
    );
  }
  if (!submission || !submission.submission_time) {
    return (
      <div className="assignment-page">
        <button className="back-btn" onClick={() => navigate(-1)}>
          ← Back to submissions
        </button>
        <div className="assignment-main">
          <div className="assignment-left">
            <h1 className="assignment-title">Submission not found</h1>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="assignment-page">
  <button className="back-btn" onClick={() => navigate(-1)}>
    ← Back to submissions
  </button>
  <div className="assignment-main">
    <div className="assignment-left">
      <div className="assignment-date">
        <span style={{ fontWeight: 'bold', marginRight: 8 }}>Submitted at:</span>
        {submission.submission_time}
      </div>
      <h1 className="assignment-title">
        {submission.student_name || submission.student_email || student_email}
      </h1>

      <div className="grade-block">
        <div className="grade-block-title">Grade and comment:</div>
        <div className="grade-form">
          <input
            type="text"
            placeholder="Grade (any value)"
            value={grade}
            onChange={e => setGrade(e.target.value)}
            disabled={loading || success}
          />
          <textarea
            placeholder="Comment (not sent anywhere, just for view)"
            value={comment}
            onChange={e => setComment(e.target.value)}
            rows={3}
            disabled={loading || success}
          />
          <button
  className={`submit-btn ${success ? "submit-success" : ""}`}
  onClick={handleGradeSubmit}
  disabled={loading || success}
>
  {success ? "Grade added successfully" : "Grade"}
</button>
        </div>
        {loading && <div className="loading-indicator">Submitting...</div>}
      </div>
    </div>

    <div className="assignment-right">
      <div className="my-comment assignment-desc">
        <span style={{ fontWeight: 'bold', marginRight: 8 }}>Submission text:</span><br />
        <span dangerouslySetInnerHTML={{ __html: formatText(submission.comment) }} />
      </div>
      <div className="my-comment assignment-desc">
        <span style={{ fontWeight: 'bold', marginRight: 8 }}>Attachments</span><br />
        {attachments.length === 0 ? (
          <span> No attachments </span>
        ):(
          attachments.map((file, index) => (
            <div key={index} style={{ marginBottom: '8px' }}>
              <button
                onClick={() => downloadAttachment(file.file_id)}
                className="link-style-button"
              >
                {file.filename}
              </button>
              <div className="assignment-date">
                <span style={{ fontWeight: 'bold', marginRight: 8 }}>Uploaded at:</span>
                {file.upload_time}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  </div>
</div>

  );
}
