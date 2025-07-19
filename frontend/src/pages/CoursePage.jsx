import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import axios from "axios"
import PageMeta from "../components/PageMeta"
import "../styles/CoursePage.css"
import Header from "../components/Header"
import CourseFeed from "../components/CourseFeed"
import AddMaterial from "../components/AddMaterial"
import AddAssignment from "../components/AddAssignment"
import AddStudent from "../components/AddStudent"
import AddTeacher from "../components/AddTeacher"
import AddParent from "../components/AddParent"
import LeaveCourse from "../components/LeaveCourse"
import SingleCourseFeed from "../components/SingleCourseFeed"
import CourseTabs from "../components/CoursesTabs"
import "../styles/UnifiedButtons.css"



export default function CoursePage() {
  const { id } = useParams();
  const [courseInfo, setCourseInfo] = useState(null);
  const [showMaterialModal, setShowMaterialModal] = useState(false);
  const [showAddAssignment, setShowAddAssignment] = useState(false);
  const [showAddStudent, setShowAddStudent] = useState(false);
  const [showAddTeacher, setShowAddTeacher] = useState(false);
  const [showAddParent, setShowAddParent] = useState(false);
  const [roleData, setRoleData] = useState();
  const [ownEmail, setOwnEmail] = useState("");
  const [showLeaveCourse, setShowLeaveCourse] = useState();
  const [singleColumnSwitch, setSingleColumnSwitch] = useState(false);
  const [activeTab, setActiveTab] = useState("Course");
  const [teachers, setTeachers] = useState([]);
  const [loadingTeachers, setLoadingTeachers] = useState(false);

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const res = await axios.get("/api/get_course_info", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id },
        });
        setCourseInfo(res.data);
      } catch (err) {
        alert("Error loading course: " + (err.response?.data?.detail || err.message));
      }
    };
    fetchCourse();

    const fetchRoleData = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const res = await axios.get("/api/get_user_role", {
          headers: { Authorization: `Bearer ${token}` },
          params: { course_id: id },
        });
        setRoleData(res.data);
      } catch (err) {
        alert("Error loading user role: " + (err.response?.data?.detail || err.message));
      }
    };
    fetchRoleData();

    const fetchEmail = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const res = await axios.get("/api/get_user_info", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setOwnEmail(res.data.email);
      } catch (err) {
        alert("Error loading email: " + (err.response?.data?.detail || err.message));
      }
    };
    fetchEmail();
  }, [id]);

  useEffect(() => {
    if (activeTab === "Participants") {
      setLoadingTeachers(true);
      const fetchTeachers = async () => {
        try {
          const token = localStorage.getItem("access_token");
          const res = await axios.get("/api/get_course_teachers", {
            headers: { Authorization: `Bearer ${token}` },
            params: { course_id: id },
          });
          setTeachers(res.data);
        } catch (err) {
          alert("Error loading teachers: " + (err.response?.data?.detail || err.message));
        } finally {
          setLoadingTeachers(false);
        }
      };
      fetchTeachers();
    }
  }, [activeTab, id]);

  const handleRemoveTeacher = async (teacherEmail) => {
    if (!window.confirm("Are you sure you want to remove this teacher?")) return;
    try {
      const token = localStorage.getItem("access_token");
      await axios.post("/api/remove_teacher", null, {
        headers: { Authorization: `Bearer ${token}` },
        params: { course_id: id, teacher_email: teacherEmail },
      });
      setTeachers((prev) => prev.filter((t) => t.email !== teacherEmail));
    } catch (err) {
      alert("Error removing teacher: " + (err.response?.data?.detail || err.message));
    }
  };

  if (!courseInfo) return <div>Loading course...</div>;

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
        {activeTab === "Course" && (
          <>
            <p><strong>Created:</strong> {new Date(courseInfo.creation_time).toLocaleDateString()}</p>
            <p>Students enrolled: {courseInfo.number_of_students}</p>
            {roleData && (roleData.is_teacher || roleData.is_admin) && (
              <div className="actions-flex">
                <div className="combo-button green" onClick={() => setShowMaterialModal(true)}>
                  + Add <span className="divider">Material</span><span className="divider-separator">|</span><span className="divider" onClick={(e) => {
                    e.stopPropagation()
                    setShowAddAssignment(true)
                  }}>Assignment</span>
                </div>

                <div className="combo-button green" onClick={() => setShowAddStudent(true)}>
                  + Add <span className="divider">Student</span><span className="divider-separator">|</span>
                  <span className="divider" onClick={(e) => {
                    e.stopPropagation()
                    setShowAddTeacher(true)
                  }}>Teacher</span><span className="divider-separator">|</span>
                  <span className="divider" onClick={(e) => {
                    e.stopPropagation()
                    setShowAddParent(true)
                  }}>Parent</span>
                </div>
                {!roleData.is_admin && (
                  <button className="outlined-btn red" onClick={() => setShowLeaveCourse(true)}>Leave Course</button>
                )}
                <button className="outlined-btn blue" onClick={() => setSingleColumnSwitch(!singleColumnSwitch)}>Switch</button>
              </div>
            )}
            {roleData && !roleData.is_admin &&(roleData.is_student || roleData.is_parent ) && (
              <div className="actions-flex">
                <button className="outlined-btn red" onClick={() => setShowLeaveCourse(true)}>Leave Course</button>
                <button className="outlined-btn blue" onClick={() => setSingleColumnSwitch(!singleColumnSwitch)}>Switch</button>
              </div>
            )}
            {!singleColumnSwitch&&(<CourseFeed />)}
            {singleColumnSwitch&&(<SingleCourseFeed />)}
          </>
        )}
        {activeTab === "Participants" && (
          <div className="participants-list">
            <h2>Teachers</h2>
            {loadingTeachers ? (
              <div>Loading teachers...</div>
            ) : (
              <ul>
                {teachers.map((teacher) => (
                  <li key={teacher.email} className="teacher-item">
                    <span>{teacher.name} ({teacher.email})</span>
                    {roleData && roleData.is_teacher && teacher.email !== ownEmail && (
                      <button
                        className="remove-teacher-btn"
                        title="Remove teacher"
                        onClick={() => handleRemoveTeacher(teacher.email)}
                      >
                        ×
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
        {activeTab === "Grades" && (
          <div className="grades-placeholder">
            <h2>Grades</h2>
            <p>Grades view coming soon...</p>
          </div>
        )}
      </div>

      {showMaterialModal && (
        <AddMaterial
          onClose={() => setShowMaterialModal(false)}
          courseId={id}
          onSuccess={() => window.location.reload()}
        />
      )}
      {showAddAssignment && (
        <AddAssignment
          onClose={() => setShowAddAssignment(false)}
          courseId={id}
          onSuccess={() => window.location.reload()}
        />
      )}
      {showAddStudent && (
        <AddStudent
          onClose={() => setShowAddStudent(false)}
          courseId={id}
        />
      )}
      {showAddTeacher && (
        <AddTeacher
          onClose={() => setShowAddTeacher(false)}
          courseId={id}
        />
      )}
      {showAddParent && (
        <AddParent
          onClose={() => setShowAddParent(false)}
          courseId={id}
        />
      )}
      {showLeaveCourse && (
        <LeaveCourse
          onClose={() => setShowLeaveCourse(false)}
          courseId={id}
          roleData={roleData}
          ownEmail={ownEmail}
        />
      )}
    </Header>
  );
}
