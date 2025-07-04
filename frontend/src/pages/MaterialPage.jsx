import React, { useEffect, useState } from "react"
import "../styles/MaterialPage.css"
/*TODO: UPDATE STYLES NEXT WEEK */
import {useParams} from "react-router-dom"
import axios from "axios"

export default function MaterialPage({
  role = "teacher", // "teacher" | "student" | "parent"
  submissions = [], // [{ studentName, comment, grade, gradedBy }]
  mySubmission = null, // { comment, grade, gradedBy }
  onBack,
}) {
  const { post_id , id: course_id} = useParams()
  const [material,setMaterial] = useState()

  useEffect (() => {
    const fetchMaterial = async () => {
      try{
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/api/get_material", {
          headers:{ Authorization: `Bearer ${token}` },
          params: { material_id: post_id , course_id }
        })
        setMaterial(res.data)
      }catch (err) {
        console.log("Material fetch error:", err.response?.data);
        alert("Ошибка при загрузке задания: " + (
          typeof err.response?.data?.detail === "string"
            ? err.response.data.detail
            : JSON.stringify(err.response?.data?.detail || err.message)
    ))
}
    }
    fetchMaterial()
  }, [post_id,course_id])

if (!material) {
    return <div>Loading...</div>;
  }

  return (
    <div className="assignment-page">
      <a href="../">
        <button className="back-btn">← Back to course feed</button>
      </a>
      <div className="assignment-main">
        <div className="assignment-left">
          <h1>{material.title}</h1>
          <p>{material.description}</p>
          <p>Material ID : {material.material_id}</p>
          <p>Created : {material.creation_time}</p>
        </div>
      </div>

    </div>
  )
}
