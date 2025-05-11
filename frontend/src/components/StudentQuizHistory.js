import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import "./StudentQuizHistory.css";

const StudentQuizHistory = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchQuizHistory = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/student/categories/${id}/quizzes/history/`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        setQuizzes(response.data || []);
      } catch (error) {
        setError(error.response?.data?.error || "Failed to load quiz history");
        setQuizzes([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchQuizHistory();
  }, [id]);

  const handleBack = () => {
    navigate(`/student/categories/${id}`);
  };

  if (isLoading) return <div className="loading">Loading quiz history...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="quiz-history-container">
      <nav className="navbar">
        <div className="navbar-left">
          <span className="logo">Quizly</span>
        </div>
        <div className="navbar-right">
          <button className="back-button" onClick={handleBack}>
            Back to Module
          </button>
        </div>
      </nav>

      <div className="quiz-history-content">
        <h1>Quiz History</h1>

        {quizzes.length === 0 ? (
          <div className="no-quizzes">No quizzes attempted in this module</div>
        ) : (
          <div className="quizzes-list">
            {quizzes.map((quiz) => (
              <div key={quiz.id} className="quiz-card">
                <h3>{quiz.titre}</h3>
                <div className="quiz-meta">
                  <span>
                    Date passed:{" "}
                    {new Date(quiz.date_passee).toLocaleDateString()}
                  </span>
                  <span>
                    Score: {quiz.note} / {quiz.sur}
                  </span>
                </div>
                <button
                  className="view-details"
                  onClick={() =>
                    navigate(
                      `/student/categories/${id}/quizzes/${quiz.id}/result`
                    )
                  }
                >
                  View Result
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentQuizHistory;
