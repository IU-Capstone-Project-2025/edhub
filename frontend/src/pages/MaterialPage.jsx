import React, { useEffect, useState ,useRef} from "react"
import "../styles/MaterialPage.css"
import {useParams, useNavigate} from "react-router-dom"
import axios from "axios"
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

export default function MaterialPage() {
  const { post_id , id: course_id} = useParams()
  const [material,setMaterial] = useState()
  const [roleData, setRoleData] = useState()
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [materialAttachments, setMaterialAttachments] = useState([]);
  const fileInputRef = useRef(null);

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
        alert("Error loading material: " + (err.response?.data?.detail || err.message))
        console.log("Error loading material: " + (err.response?.data?.detail || err.message));
        navigate("/courses/" + course_id);
}
    }
    fetchMaterial()
  }, [post_id,course_id])

  const uploadMaterialAttachment = async()=>{
    try{
      const token = localStorage.getItem("access_token")
      if (selectedFile){
        const formData = new FormData();
        formData.append("file", selectedFile, selectedFile.name);
        await axios.post("/api/create_material_attachment", formData, {
          headers: { Authorization: `Bearer ${token}` },
          params:{ course_id, material_id: post_id}
        })
      }
      fetchMaterialAttachments();
    }catch(err){
      alert("Error uploading attachment: " + (err.response?.data?.detail || err.message))
    }
  }

  const fetchMaterialAttachments = async () => {
    try{
      const token = localStorage.getItem("access_token")
      const res = await axios.get("/api/get_material_attachments", {
        headers: { Authorization: `Bearer ${token}` },
        params: { course_id, material_id: post_id }
      })
      setMaterialAttachments(res.data || [])
    }catch(err){
      alert("Error fetching attachment: " + (err.response?.data?.detail || err.message))
      setMaterialAttachments([]);
    }
  }
  
  useEffect(() => {
    if (material) {
      fetchMaterialAttachments();
    }
  }, [material]);

  const downloadAttachment = async (file_id) => {
    try {
      const token = localStorage.getItem("access_token");
  
      const response = await axios.get("/api/download_material_attachment", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        params: {
          course_id,
          material_id: post_id,
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
      const date = new Date(selectedFile?.lastModified)
      return (
        <div>
          <h2>File Details:</h2>
          <p>File Name: {selectedFile.name}</p>
          <p>File Type: {selectedFile?.type || "MIME type omitted"}</p>
          <p>
            Last Modified: {date.toLocaleString() || "Not available"}
          </p>
        </div>
      );
    }
  }

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
                            alert("Error deleting material: " + (err.response?.data?.detail || err.message))
                          }
                        }
                      }}
                    >
                      Delete material
                    </div>
                  )}
          <p className="assignment-desc" dangerouslySetInnerHTML={{__html: formatText(material.description)}} />
          <div className="my-comment assignment-desc">
            <span style={{ fontWeight: 'bold', marginRight: 8 }}>Attachments</span><br />
            {materialAttachments?.length ===0 ? (
              <span>No attachments uploaded yet.</span>
            ) : (
              <ul className="submission-list">
                {materialAttachments?.map((attachment) => (
                  <li key={attachment.file_id}>
                    <button
                      className="link-style-button"
                      onClick={() => downloadAttachment(attachment.file_id)}
                    >
                      {attachment.filename}
                    </button>
                  </li>
                ))}
              </ul>
            )}
            {material && roleData && roleData?.is_teacher && materialAttachments.length ===0 &&(
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
                    onClick={uploadMaterialAttachment}
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
      </div>

    </div>
  )
}
