import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";
import "../styles/CourseFeed.css";

export default function CourseFeed() {
  const { id } = useParams();
  const [materials, setMaterials] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchFeed = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const res = await axios.get("/get_course_feed", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id },
        });
        const feed = res.data;
        setMaterials(feed.filter(item => item.type === "mat"));
        setAssignments(feed.filter(item => item.type === "ass"));
      } catch (err) {
        setMaterials([]);
        setAssignments([]);
      }
    };
    fetchFeed();
  }, [id]);

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
              onClick={() => navigate(`/materials/${mat.post_id}`)}
            >
              {mat.title || mat.post_id}
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
              onClick={() => navigate(`/assignments/${ass.post_id}`)}
            >
              {ass.title || ass.post_id}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
