import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Import des composants
import LandingPage from "./LandingPage";
import Login from "./Login";
import SignUp from "./SignUp";
import TeacherOrStudent from "./TeacherOrStudent";
import TeacherModuleDetail from "./TeacherModuleDetail";
import TeacherModules from "./TeacherModules";
import TeacherQuizHistory from "./TeacherQuizHistory";
import TeacherQuizDetail from "./TeacherQuizDetail";

// Import des composants pour les étudiants
import StudentCategories from "./StudentCategories"; // Liste des modules étudiant
import StudentCategoryDetail from "./StudentCategoryDetail"; // Détail du module étudiant
import StudentQuizDetail from "./StudentQuizDetail"; // Détail du quiz étudiant
import StudentQuizHistory from "./StudentQuizHistory"; // Historique des quiz étudiant

function App() {
  return (
    <div>
      <Routes>
        {/* Routes pour les étudiants */}
        <Route path="/student/categories" element={<StudentCategories />} />
        <Route
          path="/student/categories/:id"
          element={<StudentCategoryDetail />}
        />
        <Route
          path="/student/categories/:id/quizzes"
          element={<StudentQuizHistory />}
        />
        <Route
          path="/student/quizzes/:quizId"
          element={<StudentQuizDetail />}
        />
      </Routes>
    </div>
  );
}

export default App;
