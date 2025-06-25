import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AuthPage from "./pages/AuthPage";
import CoursesPage from "./pages/CoursesPage";
import CoursePage from "./pages/CoursePage";
import AssignmentPage from "./pages/AssignmentPage";
import MaterialPage from "./pages/MaterialPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AuthPage />} />
        <Route path="/courses" element={<CoursesPage />} />
        <Route path="/courses/:id" element={<CoursePage />} /> 
        <Route path="/courses/:id/materials/:post_id" element={<MaterialPage/>} />
        <Route path="/courses/:id/assignments/:post_id" element={<AssignmentPage />} />
      </Routes>
    </Router>
  );
}

export default App;
