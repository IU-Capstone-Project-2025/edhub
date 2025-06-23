import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AuthPage from "./pages/AuthPage";
import CoursesPage from "./pages/CoursesPage";
import CreateCoursePage from "./components/CreateCourse";
import CoursePage from "./pages/CoursePage";

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
  );
}

export default App;
