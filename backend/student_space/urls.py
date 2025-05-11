from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    # Redirection et dashboard
    path('', views.student_dashboard, name='student_dashboard'),
    path('after-login/', views.after_login_redirect, name='after_login'),
    
    # Gestion des catégories/modules
    path('categories/', views.student_categories, name='student_categories'),
    path('categories/check/', views.check_student_categories, name='check_student_categories'),
    path('categories/create/', views.create_category, name='create_category'),
    
    # Modules et quizzes
    path('categories/<int:category_id>/quizzes/', views.available_quizzes, name='student-category-quizzes'),
    path('categories/<int:category_id>/quizzes/history/', views.student_quiz_history, name='student-quiz-history'),
    
    # Gestion des quizzes
    path('quizzes/<int:quiz_id>/start/', views.start_quiz_attempt, name='start-quiz-attempt'),
    path('quizzes/<int:quiz_id>/results/', views.quiz_results, name='quiz-results'),
    
    # Gestion des tentatives
    path('attempts/<int:attempt_id>/', views.attempt_detail, name='attempt-detail'),
    path('attempts/<int:attempt_id>/submit/', views.submit_quiz_answer, name='submit-quiz-answer'),
    path('attempts/<int:attempt_id>/finish/', views.finish_quiz_attempt, name='finish-quiz-attempt'),
    
    # Ressources
    path('pdfs/<int:pdf_id>/download/', views.download_pdf, name='download-pdf'),
    
    # Fonctionnalités supplémentaires
    path('questions/<int:question_id>/explanation/', views.get_question_explanation, name='question-explanation'),
]