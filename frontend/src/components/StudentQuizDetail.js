import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import "./StudentQuizDetail.css"; // tu peux renommer la CSS si besoin

const StudentQuizDetail = () => {
  const { id, quizId } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    const fetchQuiz = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(
          `http://localhost:8000/student/quizzes/${quizId}/`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        setQuiz(response.data);
      } catch (error) {
        setError(error.response?.data?.error || "Failed to load quiz");
      } finally {
        setIsLoading(false);
      }
    };

    fetchQuiz();
  }, [quizId]);

  const handleAnswerChange = (questionId, choiceId) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: choiceId,
    }));
  };

  const handleSubmit = async () => {
    const payload = {
      quiz_id: quizId,
      answers: answers,
    };

    try {
      await axios.post(
        `http://localhost:8000/student/quizzes/${quizId}/submit/`,
        payload,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
            "Content-Type": "application/json",
          },
        }
      );
      setSubmitted(true);
    } catch (error) {
      setError(error.response?.data?.error || "Failed to submit answers");
    }
  };

  const handleBack = () => {
    navigate(`/student/categories/${id}`);
  };

  if (isLoading) return <div className="loading">Loading quiz...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!quiz) return <div className="error">Quiz not found</div>;

  return (
    <div className="quiz-detail-container">
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

      <div className="quiz-detail-content">
        <h1>{quiz.titre}</h1>
        <p className="quiz-description">{quiz.description}</p>

        <div className="questions-section">
          <h2>Questions</h2>
          {quiz.questions.map((question, qIndex) => (
            <div key={question.id} className="question-card">
              <h3>
                Question {qIndex + 1}: {question.enonce}
              </h3>
              <ul className="choices-list">
                {question.choix.map((choice) => (
                  <li key={choice.id}>
                    <label>
                      <input
                        type="radio"
                        name={`question-${question.id}`}
                        value={choice.id}
                        disabled={submitted}
                        checked={answers[question.id] === choice.id}
                        onChange={() =>
                          handleAnswerChange(question.id, choice.id)
                        }
                      />
                      {choice.texte}
                    </label>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {!submitted ? (
          <button className="submit-button" onClick={handleSubmit}>
            Submit Answers
          </button>
        ) : (
          <p className="submitted-message">Your answers have been submitted!</p>
        )}
      </div>
    </div>
  );
};

export default StudentQuizDetail;
