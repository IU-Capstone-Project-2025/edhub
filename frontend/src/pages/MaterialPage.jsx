import React, { useEffect, useState } from "react"
import "../styles/MaterialPage.css"
import {useParams} from "react-router-dom"
import axios from "axios"
import PageMeta from "../components/PageMeta"
import "../styles/AssignmentPage.css"

function formatText(text) {
  if (!text) return "";
  let html = text
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>') // bold: **text**
    .replace(/__(.*?)__/g, '<u>$1</u>') // underline: __text__
    .replace(/\*(.*?)\*/g, '<i>$1</i>'); // italic: *text*
  return html;
}

export default function MaterialPage() {
  const { post_id , id: course_id} = useParams()
  const [material,setMaterial] = useState()
  const [roleData, setRoleData] = useState()

  useEffect(() => {
    const fetchRoleData = async () => {
      try {
        const token = localStorage.getItem("access_token")
        const res = await axios.get("/api/get_user_role", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id },
        })
        setRoleData(res.data)
      } catch (err) {
        // ignore
      }
    }
    fetchRoleData()
  }, [course_id])
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
      <PageMeta title={material.title} icon="/edHub_icon.svg" />
      <a href="../">
        <button className="back-btn">← Back to course feed</button>
      </a>
      <div className="assignment-main">
        <div className="assignment-left">
          <div className="assignment-date">{material.creation_time}</div>
          <h1 className="assignment-title">{material.title}</h1>
                    {roleData && (roleData.is_teacher || roleData.is_admin) && (
                    <div
                      className="remove-assignment-text"
                      onClick={async () => {
                        if (window.confirm("Are you sure you want to remove this material? This action cannot be undone.")) {
                          try {
                            const token = localStorage.getItem("access_token")
                            await axios.post("/api/remove_material", null, {
                              headers: { Authorization: `Bearer ${token}` },
                              params: { course_id, material_id: post_id }
                            })
                            window.location.assign("../")
                          } catch (err) {
                            alert("Ошибка при удалении материала: " + (err.response?.data?.detail || err.message))
                          }
                        }
                      }}
                    >
                      Delete material
                    </div>
                  )}
          <p className="assignment-desc" dangerouslySetInnerHTML={{__html: formatText(material.description)}} />
        </div>
      </div>

    </div>
  )
}
