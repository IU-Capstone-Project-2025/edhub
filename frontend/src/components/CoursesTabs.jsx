import React from "react"
import { useNavigate, useParams } from "react-router-dom"
import "./../styles/CourseTabs.css"

export default function CourseTabs({ activeTab, onTabChange, availableTabs }) {
  const navigate = useNavigate();
  const { id } = useParams();
  const handleTabClick = (tab) => {
    if (tab === "Participants" && id) {
      navigate(`/courses/${id}/participants`);
    } else if (tab === "Grades" && id) {
      navigate(`/courses/${id}/grades`);
    } else if (tab === "Course" && id) {
      navigate(`/courses/${id}`);
    } else {
      onTabChange && onTabChange(tab);
    }
  };
  return (
    <div className="course-tabs">
      {availableTabs.map((tab) => (
        <button
          key={tab}
          className={`course-tab-button ${activeTab === tab ? "active" : ""}`}
          onClick={() => handleTabClick(tab)}
        >
          {tab}
        </button>
      ))}
    </div>
  )
}
