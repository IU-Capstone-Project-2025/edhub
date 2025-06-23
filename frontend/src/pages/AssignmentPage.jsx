import React, { useEffect, useState } from "react"
import "./AssignmentPage.css"

export default function AssignmentPage({
  role = "teacher", // "teacher" | "student" | "parent"
  assignment = { title: "Assignment Title", description: "Assignment description goes here." },
  submissions = [], // [{ studentName, comment, grade, gradedBy }]
  mySubmission = null, // { comment, grade, gradedBy }
  onSubmit,
  onGrade,
  onBack,
}) {
  const [popup, setPopup] = useState(null)
  const [input, setInput] = useState("")
  const [grade, setGrade] = useState("")

  // Pop-up for teacher/parent: show submission, grade button
  const handleOpenPopup = (submission) => setPopup(submission)
  const handleClosePopup = () => setPopup(null)
  const handleGrade = () => {
    onGrade && onGrade(popup, grade)
    setGrade("")
    setPopup(null)
  }

  return (
    <div className="assignment-page">
      <button className="back-btn" onClick={onBack}>← Back to course feed</button>
      <div className="assignment-main">
        <div className="assignment-left">
          <h1>{assignment.title}</h1>
          <p>{assignment.description}</p>
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
