import React from "react"
import { FaTimes } from "react-icons/fa"
import "./../styles/ParticipantsView.css"

export default function ParticipantsView({ participants, role, onRemoveStudent, onRemoveParent }) {
  return (
    <div className="participants-view">
      <h2>Participants</h2>
      <div className="students-list">
        {participants.map((student) => (
          <div className="student-block" key={student.id}>
            <div className="student-info">
              <div>
                <div className="name">{student.name}</div>
                <div className="email">{student.email}</div>
              </div>
              {role === "teacher" && (
                <FaTimes className="remove-icon" onClick={() => onRemoveStudent(student.id)} />
              )}
            </div>

            {role === "teacher" && student.parents && student.parents.length > 0 && (
              <div className="parent-list">
                {student.parents.map((parent) => (
                  <div className="parent-block" key={parent.id}>
                    <div>
                      <div className="name">{parent.name}</div>
                      <div className="email">{parent.email}</div>
                    </div>
                    <FaTimes
                      className="remove-icon"
                      onClick={() => onRemoveParent(student.id, parent.id)}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
