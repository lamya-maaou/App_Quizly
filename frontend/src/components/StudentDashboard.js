import React from "react";
import { BrowserRouter as Routes, Route } from "react-router-dom";
import "./StudentDashboard.css";
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
