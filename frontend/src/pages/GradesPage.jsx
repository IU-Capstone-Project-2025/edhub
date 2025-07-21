import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import Header from "../components/Header";
import PageMeta from "../components/PageMeta";
import CourseTabs from "../components/CoursesTabs";
import "../styles/GradesPage.css";


export default function GradesPage() {
  const { id: course_id } = useParams();
  const [courseInfo, setCourseInfo] = useState(null);
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const [students, setStudents] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [grades, setGrades] = useState({});
  const [activeTab, setActiveTab] = useState("Grades");


  useEffect(() => {
  const fetchData = async () => {
    setLoading(true);
    const token = localStorage.getItem("access_token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      const [courseRes, roleRes, csvRes] = await Promise.all([
        axios.get(`/api/get_course_info`, { headers, params: { course_id } }),
        axios.get("/api/get_user_role", { headers, params: { course_id } }),
        axios.get(`/api/download_full_course_grade_table?course_id=${course_id}`, {
          headers: { ...headers, Accept: "text/csv" },
          responseType: "blob"
        })
      ]);

      const csvText = await new Response(csvRes.data).text();
      
      if (!csvText) {
        setAssignments([]);
        setStudents([]);
        setGrades({});
        return;
      }

      const lines = csvText.trim().split(/\r?\n/);
      const parsedLines = lines.map(line => {
        const cols = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);
        return cols.map(col => col.replace(/^"|"$/g, '').trim());
      });

      const [headerRow, ...dataRows] = parsedLines;
      const assignmentTitles = headerRow.slice(2);

      const parsedStudents = [];
      const parsedGrades = {};

      for (let row of dataRows) {
        if (row.length < 3) continue;
        
        const email = row[0] || '';
        const name = row[1] || email;
        parsedStudents.push({ email, name });
        parsedGrades[email] = {};
        assignmentTitles.forEach((title, idx) => {
          const gradeValue = (idx + 2 < row.length) ? row[idx + 2] : "—";
          parsedGrades[email][title] = gradeValue || "—";
        });
      }

      setCourseInfo(courseRes.data);
      setRole(roleRes.data.role || roleRes.data);
      setStudents(parsedStudents);
      setAssignments(assignmentTitles);
      setGrades(parsedGrades);
    } catch (err) {
      console.error("Failed to load grades:", err);
    } finally {
      setLoading(false);
    }
  };

  fetchData();
}, [course_id]);

  if (loading || !courseInfo) {
    return (
      <Header>
        <div className="grades-loading">Loading grades...</div>
      </Header>
    );
  }

  return (
    <Header>
      <PageMeta title={courseInfo.title} icon="/edHub_icon.svg" />
      <div className="course-page">
        <div className="course-page-header">
          <h1 className="course-title">{courseInfo.title}</h1>
          <CourseTabs
            activeTab={activeTab}
            onTabChange={setActiveTab}
            availableTabs={["Course", "Participants", "Grades"]}
          />
        </div>

        {students.length === 0 ? (
          <div className="grades-empty-message">
            {role === "teacher" 
              ? "No grade data available for this course" 
              : "The grade information will appear here when you invite students."}
          </div>
        ) : (
          <table className="grades-table">
            <thead>
              <tr>
                <th>Student</th>
                {assignments.map((title, idx) => (
                  <th key={idx}>{title}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.email}>
                  <td>{student.name || student.email}</td>
                  {assignments.map((title, j) => (
                    <td key={j}>
                      {grades[student.email]?.[title] || <span className="grades-empty">—</span>}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </Header>
  );
}
