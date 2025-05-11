import React, { useState } from "react";
import axios from "axios";
import "./ModuleCreation.css";
import { useNavigate } from "react-router-dom";

const ModuleCreation = () => {
  const navigate = useNavigate();
  const [moduleName, setModuleName] = useState("");
  const userRole = localStorage.getItem("role"); // Récupère le rôle de l'utilisateur

  // Détermine si c'est un étudiant ou un enseignant
  const isStudent = userRole === "student";
  const endpoint = isStudent ? "categories" : "modules";
  const displayName = isStudent ? "catégorie" : "module";

  const handleCreateMaterial = async () => {
    const token = localStorage.getItem("token");

    if (!token) {
      alert("You must be logged in.");
      navigate("/login");
      return;
    }

    if (!moduleName.trim()) {
      alert(`Please enter a ${displayName} name.`);
      return;
    }

    try {
      const response = await axios.post(
        `http://localhost:8000/api/${
          isStudent ? "student" : "teacher"
        }/${endpoint}/create/`,
        { name: moduleName },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );
      console.log(`${displayName} created:`, response.data);
      alert(`${displayName} created successfully!`);
      navigate(isStudent ? "/student/categories" : "/teacher/modules");
    } catch (error) {
      console.error(`Error creating ${displayName}:`, error);
      alert(`Failed to create ${displayName}.`);
    }
  };

  return (
    <div className="quizly-app">
      <nav className="navbar">
        <div className="navbar-left">
          <span className="logo">Quizly</span>
        </div>
        <div className="navbar-right">
          <button className="add-button" onClick={handleCreateMaterial}>
            +
          </button>
        </div>
      </nav>

      <div className="content">
        <div className="empty-state">
          <div className="book-icon">
            <div className="book-cover">
              <div className="book-spine"></div>
              <div className="book-pages"></div>
            </div>
          </div>
          <h2>Add a material to get started</h2>
          <p>Create your first material to begin organizing your content</p>
          <input
            type="text"
            placeholder={`Enter ${displayName} name`}
            value={moduleName}
            onChange={(e) => setModuleName(e.target.value)}
            className="input-module-name"
          />
          <button className="create-button" onClick={handleCreateMaterial}>
            Create {displayName}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModuleCreation;
