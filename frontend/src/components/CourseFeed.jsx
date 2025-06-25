import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";
import "../styles/CourseFeed.css";



export default function CourseFeed() {
  const { id } = useParams();
  const [materials, setMaterials] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [assignmentDetails, setAssignmentDetails] = useState({});
  const [materialDetails, setMaterialDetails] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    const fetchFeed = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const res = await axios.get("/api/get_course_feed", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id },
        });
        const feed = res.data;
        const matList = feed.filter(item => item.type === "mat");
        setMaterials(matList);
        const assList = feed.filter(item => item.type === "ass");
        setAssignments(assList);

        const ass_details = {};
        for (const ass of assList) {
          try {
            const ass_detailRes = await axios.get("/api/get_assignment", {
              headers: { Authorization: `Bearer ${token}` },
              params: { assignment_id: ass.post_id, course_id: id },
            });
            ass_details[ass.post_id] = ass_detailRes.data;
          } catch (err) {
            ass_details[ass.post_id] = { title: "Ошибка загрузки", description: "" };
          }
        }
        setAssignmentDetails(ass_details)

        const mat_details = {}
        for (const mat of matList) {
          try {
            const mat_detailRes = await axios.get("/api/get_material", {
              headers: { Authorization: `Bearer ${token}` },
              params: { material_id: mat.post_id, course_id: id },
            });
            mat_details[mat.post_id] = mat_detailRes.data;
          } catch (err) {
            mat_details[mat.post_id] = { title: "Ошибка загрузки", description: "" };
          }
        }
        setMaterialDetails(mat_details)
        
      } catch (err) {
        setMaterials([]);
        setAssignments([]);
      }
    };
    fetchFeed();
  }, [id, assignments, materials]);




  return (
    <div className="course-feed-columns">
      <div className="feed-column">
        <h2>Materials</h2>
        <div className="feed-list">
          {materials.length === 0 && <div className="feed-placeholder">No materials yet</div>}
          {materials.map(mat => (
            <div
              className="feed-card"
              key={mat.post_id}
              onClick={() => navigate(`/courses/${id}/materials/${mat.post_id}`)}
            >
              <p>
                {materialDetails[mat.post_id]?.title}
              </p>
              <p>
                Material ID : {materialDetails[mat.post_id]?.material_id}
              </p>
              <p>
                Creation Date : {materialDetails[mat.post_id]?.creation_time}
              </p>
            </div>
          ))}
        </div>
      </div>
      <div className="feed-column">
        <h2>Assignments</h2>
        <div className="feed-list">
          {assignments.length === 0 && <div className="feed-placeholder">No assignments yet</div>}
          {assignments.map(ass => (
            <div
              className="feed-card"
              key={ass.post_id}
              onClick={() => navigate(`/courses/${id}/assignments/${ass.post_id}`)}
            >
              <p>
                {assignmentDetails[ass.post_id]?.title}
              </p>
              <p>
                Assignment ID : {assignmentDetails[ass.post_id]?.assignment_id}
              </p>
              <p>
                Creation Date : {assignmentDetails[ass.post_id]?.creation_time}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
