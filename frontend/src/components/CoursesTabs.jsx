import React from "react"
import "./../styles/CourseTabs.css"

export default function CourseTabs({ activeTab, onTabChange, availableTabs }) {
  return (
    <div className="course-tabs">
      {availableTabs.map((tab) => (
        <button
          key={tab}
          className={`course-tab-button ${activeTab === tab ? "active" : ""}`}
          onClick={() => onTabChange(tab)}
        >
          {tab}
        </button>
      ))}
    </div>
  )
}
