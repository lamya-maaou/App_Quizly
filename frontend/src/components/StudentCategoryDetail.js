import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";
import "./StudentCategoryDetail.css";

const StudentCategoryDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [module, setModule] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchModuleData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `http://localhost:8000/student/categories/${id}/`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        }
      );
      setModule(response.data);
    } catch (error) {
      console.error("Error fetching module data:", error);
      setError("Failed to load module data");
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  useEffect(() => {
    fetchModuleData();
  }, [fetchModuleData]);

  if (isLoading && !module)
    return <div className="loading">Loading module details...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!module) return <div className="error">Module not found</div>;

  return (
    <div className="module-detail-container">
      <nav className="navbar">
        <div className="navbar-left">
          <span className="logo">Quizly</span>
        </div>
        <div className="navbar-right">
          <button
            className="history-btn"
            onClick={() => navigate(`/student/categories/${id}/quizzes`)}
          >
            View Quiz History
          </button>
          <button
            className="back-button"
            onClick={() => navigate("/student/categories")}
          >
            Back to Modules
          </button>
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </nav>

      <div className="module-content">
        <h1 className="module-title">{module.name}</h1>
        <p className="module-description">{module.description}</p>
        {/* Tu peux ajouter ici d'autres infos du module si besoin */}
      </div>
    </div>
  );
};

export default StudentCategoryDetail;
