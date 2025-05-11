import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import "./Login.css";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Requête de connexion
      const response = await axios.post(
        "http://localhost:8000/api/auth/login/",
        { email, password },
        { headers: { "Content-Type": "application/json" } }
      );

      console.log("Full response:", response);

      const token = response.data.access;
      localStorage.setItem("token", token);

      // Récupère le rôle de l'utilisateur
      const role = response.data.user.role;
      console.log("User role:", role);

      // Fonction pour vérifier les modules selon le rôle
      const checkModules = async (role) => {
        let modulesResponse;
        const headers = { Authorization: `Bearer ${token}` };

        try {
          if (role === "teacher") {
            modulesResponse = await axios.get(
              "http://localhost:8000/api/teacher/modules/check/",
              { headers }
            );
            return modulesResponse.data.has_modules
              ? "/teacher/modules"
              : "/teacher/modules/create";
          } else if (role === "student") {
            modulesResponse = await axios.get(
              "http://localhost:8000/api/student/categories/check/",
              { headers }
            );
            return modulesResponse.data.has_modules
              ? "/student/categories/"
              : "/student/categories/create/";
          }
        } catch (error) {
          console.error("Error checking modules:", error);
          return null;
        }
      };

      // Redirection basée sur le rôle
      const redirectPath = await checkModules(role);

      if (redirectPath) {
        navigate(redirectPath);
      } else {
        // Redirection par défaut si le checkModules échoue
        navigate(
          role === "teacher" ? "/teacher/modules" : "/student/categories/"
        );
      }
    } catch (error) {
      console.error("Login error:", error);
      let errorMessage = "Login failed. Please try again.";

      if (error.response) {
        if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.non_field_errors) {
          errorMessage = error.response.data.non_field_errors.join(", ");
        }
      }

      alert(errorMessage);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <Link to="/" className="back-to-home">
          ← Back to home
        </Link>
        <div className="login-header">
          <h2>
            Welcome back to <span className="quizly-logo">Quizly</span>
          </h2>
          <p>Sign in to access your quizzes and learning materials</p>
        </div>
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>
          <div className="form-options">
            <div className="remember-me">
              <input type="checkbox" id="remember" />
              <label htmlFor="remember">Remember me</label>
            </div>
            <Link to="/forgot-password" className="forgot-password">
              Forgot password?
            </Link>
          </div>
          <button type="submit" className="login-button">
            Sign In
          </button>
        </form>
        <div className="signup-link">
          Don't have an account? <Link to="/signup">Sign up</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
