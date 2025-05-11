import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";
// Import des composants
import LandingPage from "./components/LandingPage";
import Login from "./components/Login";
import SignUp from "./components/SignUp";
import TeacherOrStudent from "./components/TeacherOrStudent";
import TeacherModuleDetail from "./components/TeacherModuleDetail";
import TeacherModules from "./components/TeacherModules";
import ModuleCreation from "./components/ModuleCreation";
import TeacherQuizHistory from "./components/TeacherQuizHistory";
import TeacherQuizDetail from "./components/TeacherQuizDetail";

// Import des composants pour les étudiants
import StudentDashboard from "./components/StudentDashboard";
import StudentCategories from "./components/StudentCategories";
import StudentCategoryDetail from "./components/StudentCategoryDetail";
import StudentQuizDetail from "./components/StudentQuizDetail";
import StudentQuizHistory from "./components/StudentQuizHistory";

function App() {
  return (
    <Router>
      <div>
        <Routes>
          {/* Routes publiques */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<TeacherOrStudent />} />
          <Route path="/signup-form" element={<SignUp />} />

          {/* Routes pour les enseignants */}
          <Route path="/teacher/modules" element={<TeacherModules />} />
          <Route path="/teacher/modules/create" element={<ModuleCreation />} />
          <Route
            path="/teacher/modules/:id"
            element={<TeacherModuleDetail />}
          />
          <Route
            path="/teacher/modules/:id/quizzes"
            element={<TeacherQuizHistory />}
          />
          <Route
            path="/teacher/modules/:id/quizzes/:quizId"
            element={<TeacherQuizDetail />}
          />
          <Route
            path="/teacher/modules/:module_id/generate_quiz"
            element={<ModuleCreation />}
          />

          {/* Routes pour les étudiants */}
          <Route path="/student/categories/" element={<StudentCategories />} />
          <Route
            path="/student/categories/create/"
            element={<ModuleCreation />}
          />
          <Route
            path="/student/categories/:id"
            element={<StudentCategoryDetail />}
          />
          <Route
            path="/student/categories/:category_id/quizzes"
            element={<StudentQuizHistory />}
          />
          <Route
            path="/student/categories/:category_id/quizzes/:quizId"
            element={<StudentQuizDetail />}
          />
          <Route
            path="/student/categories/:category_id/quizzes/:quizId/start"
            element={<StudentQuizDetail />}
          />
          <Route path="/student/dashboard" element={<StudentDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
