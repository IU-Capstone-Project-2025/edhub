import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import CoursesPage from "./pages/CoursesPage"
import RegisterPage from "./pages/RegisterPage"
import AuthPage from "./pages/AuthPage"
import CoursePage from "./pages/OneCoursePage"
import CreateCoursePage from "./pages/CreateCoursePage"
import axios from "axios"
axios.defaults.baseURL = "http://localhost:8000";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AuthPage />} />
        <Route path="/courses" element={<CoursesPage />} />
        <Route path="/create-course" element={<CreateCoursePage />} />
        <Route path="/courses/:id" element={<CoursePage />} />
      </Routes>
    </Router>
  )
}

export default App
