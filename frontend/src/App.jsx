import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import CoursesPage from "./pages/CoursesPage"
import RegisterPage from "./pages/RegisterPage"
import AuthPage from "./pages/AuthPage"
import CoursePage from "./pages/OneCoursePage"
import CreateCoursePage from "./pages/CreateCoursePage"
import axios from "axios"
import AddMaterialPage from "./pages/AddMaterialPage"
import AddStudentPage from "./pages/AddStudentPage"
import AddParentPage from "./pages/AddParentPage"
axios.defaults.baseURL = "/api/"


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AuthPage />} />
        <Route path="/courses" element={<CoursesPage />} />
        <Route path="/create-course" element={<CreateCoursePage />} />
        <Route path="/courses/:id" element={<CoursePage />} />
        <Route path="/courses/:id/add-material" element={<AddMaterialPage/>}/>
        <Route path="/courses/:id/add-student" element={<AddStudentPage />} />
        <Route path="/courses/:id/add-parent" element={<AddParentPage />} />
      </Routes>
    </Router>
  )
}

export default App
