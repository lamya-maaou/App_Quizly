from django.utils import timezone
from typing import Self
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from django.conf import settings
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from student_space.models import Module, PDF, Quiz, Question, Choix
from .models import StudentProgress, StudentQuizAttempt, StudentAnswer
from .serializers import (
    ModuleSerializer,
    StudentQuizSerializer,
    StudentQuizDetailSerializer,
    StudentAttemptSerializer
)




# Vue de redirection après login
def after_login_redirect(request):
    if request.user.is_authenticated:
        if request.user.role == 'student':
            modules = Module.objects.filter(student=request.user)
            if modules.exists():
                return redirect('/student/modules')  # url vers la liste des modules
            else:
                return redirect('/student-create-module')  # url vers la création de module
        elif request.user.role == 'teacher':
            return redirect('teacher_dashboard')  # par exemple
        elif request.user.role == 'admin':
            return redirect('admin_dashboard')  # par exemple
    else:
        return redirect('login')

# Vues pour les modules
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_student_categories(request):
    user = request.user
    if user.role != 'student':
        return Response({'error': 'Unauthorized access'}, status=403)
    
    # Vérifie si ce student a des modules
    has_modules = Module.objects.filter(student=user).exists()
    
    return Response({'has_modules': True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category(request):
    if request.user.role != 'student':
        return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

    name = request.data.get('name')
    if not name:
        return Response({'error': 'Module name is required'}, status=status.HTTP_400_BAD_REQUEST)

    module =Module.objects.create(name=name, student=request.user)
    return Response(ModuleSerializer(module).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_categories(request):
    if request.user.role != 'student':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    modules = Module.objects.filter(student=request.user)
    return Response(ModuleSerializer(modules, many=True).data)


# Vue de tableau de bord étudiant
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    if request.user.role != 'student':
        return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)
    
    # Modules disponibles pour l'étudiant
    modules = Module.objects.all()
    progress_data = []
    
    for module in modules:
        progress, _ = StudentProgress.objects.get_or_create(
            student=request.user,
            module=module
        )
        progress_data.append({
            'module': ModuleSerializer(module).data,
            'progress': {
                'completed': progress.completed,
                'completion_date': progress.completion_date
            }
        })
    
    return Response({
        'modules': progress_data,
        'active_attempts': StudentQuizAttempt.objects.filter(
            student=request.user,
            end_time__isnull=True
        ).count()
    })

# Vues pour les modules étudiants
#@api_view(['GET'])
#@permission_classes([IsAuthenticated])
#def student_categories(request):
  #  if request.user.role != 'student':
  #      return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
 #   
 #   modules = Module.objects.all()
#    serializer = ModuleSerializer(modules, many=True)
#   return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_category_detail(request, pk):
    try:
        module = Module.objects.get(id=pk)
        progress, _ = StudentProgress.objects.get_or_create(
            student=request.user,
            module=module
        )
        
        # Récupérer les PDFs et quiz du module
        pdfs = PDF.objects.filter(module=module)
        quizzes = Quiz.objects.filter(module=module)
        
        response_data = {
            'module': ModuleSerializer(module).data,
            'progress': {
                'completed': progress.completed,
                'completion_date': progress.completion_date
            },
            'resources': {
                'pdfs': [{
                    'id': pdf.id,
                    'title': pdf.titre,
                    'url': request.build_absolute_uri(pdf.fichier.url)
                } for pdf in pdfs],
                'quizzes': StudentQuizSerializer(quizzes, many=True).data
            }
        }
        
        return Response(response_data)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)

# Vues pour les quiz étudiants
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_quizzes(request, module_id):
    if request.user.role != 'student':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    quizzes = Quiz.objects.filter(module__id=module_id)
    return Response(StudentQuizSerializer(quizzes, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_quiz_attempt(request, quiz_id):
    if request.user.role != 'student':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        
        # Vérifier s'il y a déjà une tentative en cours
        existing_attempt = StudentQuizAttempt.objects.filter(
            student=request.user,
            quiz=quiz,
            end_time__isnull=True
        ).first()
        
        if existing_attempt:
            return Response({
                'attempt_id': existing_attempt.id,
                'message': 'Continuing existing attempt'
            })
            
        # Créer une nouvelle tentative
        attempt = StudentQuizAttempt.objects.create(
            student=request.user,
            quiz=quiz
        )
        
        return Response({
            'attempt_id': attempt.id,
            'quiz': StudentQuizDetailSerializer(quiz).data
        })
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz_answer(request, attempt_id):
    if request.user.role != 'student':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        attempt = StudentQuizAttempt.objects.get(id=attempt_id, student=request.user)
        question_id = request.data.get('question_id')
        choice_id = request.data.get('choice_id')
        
        if not question_id or not choice_id:
            return Response({'error': 'Missing question_id or choice_id'}, status=status.HTTP_400_BAD_REQUEST)
            
        question = Question.objects.get(id=question_id, quiz=attempt.quiz)
        choice = Choix.objects.get(id=choice_id, question=question)
        
        # Enregistrer la réponse
        StudentAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={'choice': choice}
        )
        
        return Response({'status': 'Answer saved'})
    except (StudentQuizAttempt.DoesNotExist, Question.DoesNotExist, Choix.DoesNotExist) as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finish_quiz_attempt(request, attempt_id):
    if request.user.role != 'student':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        attempt = StudentQuizAttempt.objects.get(id=attempt_id, student=request.user)
        
        if attempt.end_time:
            return Response({'error': 'Attempt already finished'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Calculer le score
        attempt.score = attempt.calculate_score()
        attempt.end_time = timezone.now()
        attempt.save()
        
        # Mettre à jour la progression
        Self._update_student_progress(request.user, attempt.quiz.module)
        
        return Response(StudentAttemptSerializer(attempt).data)
    except StudentQuizAttempt.DoesNotExist:
        return Response({'error': 'Attempt not found'}, status=status.HTTP_404_NOT_FOUND)

def _update_student_progress(self, student, module):
    # Vérifier si tous les quiz du module sont complétés
    quizzes = Quiz.objects.filter(module=module)
    completed_quizzes = StudentQuizAttempt.objects.filter(
        student=student,
        quiz__in=quizzes,
        end_time__isnull=False
    ).values_list('quiz', flat=True).distinct()
    
    if set(quizzes.values_list('id', flat=True)) == set(completed_quizzes):
        progress, _ = StudentProgress.objects.get_or_create(
            student=student,
            module=module
        )
        if not progress.completed:
            progress.completed = True
            progress.completion_date = timezone.now()
            progress.save()

# Vues pour les résultats
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_results(request, quiz_id):
    if request.user.role != 'student':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    attempts = StudentQuizAttempt.objects.filter(
        student=request.user,
        quiz__id=quiz_id,
        end_time__isnull=False
    ).order_by('-end_time')
    
    return Response(StudentAttemptSerializer(attempts, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attempt_detail(request, attempt_id):
    if request.user.role != 'student':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        attempt = StudentQuizAttempt.objects.get(id=attempt_id, student=request.user)
        answers = StudentAnswer.objects.filter(attempt=attempt).select_related('question', 'choice')
        
        response_data = StudentAttemptSerializer(attempt).data
        response_data['answers'] = []
        
        for answer in answers:
            response_data['answers'].append({
                'question': answer.question.enonce,
                'selected_choice': answer.choice.texte,
                'is_correct': answer.choice.is_correct,
                'correct_choices': list(answer.question.choix.filter(is_correct=True).values_list('texte', flat=True))
            })
        
        return Response(response_data)
    except StudentQuizAttempt.DoesNotExist:
        return Response({'error': 'Attempt not found'}, status=status.HTTP_404_NOT_FOUND)

# Vue pour télécharger un PDF
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_pdf(request, pdf_id):
    try:
        pdf = PDF.objects.get(id=pdf_id)
        file_path = os.path.join(settings.MEDIA_ROOT, str(pdf.fichier))
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    except PDF.DoesNotExist:
        return Response({'error': 'PDF not found'}, status=status.HTTP_404_NOT_FOUND)
    

from .services.gemini_service import StudentGeminiService

def get_question_explanation(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        attempt = StudentQuizAttempt.objects.get(student=request.user, quiz=question.quiz)
        answer = StudentAnswer.objects.get(attempt=attempt, question=question)
        
        gemini = StudentGeminiService()
        explanation = gemini.get_explanation_for_question(
            question_text=question.enonce,
            student_answer=answer.choice.texte,
            correct_answer=question.choix.filter(is_correct=True).first().texte
        )
        
        return Response(explanation)
        
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_quiz_history(request, module_id):
    if request.user.role != 'student':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    # Filtrer les tentatives terminées pour ce module
    attempts = StudentQuizAttempt.objects.filter(
        student=request.user,
        quiz__module__id=module_id,
        end_time__isnull=False
    ).select_related('quiz').order_by('-end_time')

    # Regrouper par quiz unique (le dernier en date)
    seen_quiz_ids = set()
    quiz_history = []

    for attempt in attempts:
        if attempt.quiz.id not in seen_quiz_ids:
            seen_quiz_ids.add(attempt.quiz.id)
            quiz_data = {
                'id': attempt.quiz.id,
                'titre': attempt.quiz.titre,
                'description': attempt.quiz.description,
                'date_creation': attempt.quiz.date_creation,
                'questions_count': attempt.quiz.questions.count()
            }
            quiz_history.append(quiz_data)

    return Response(quiz_history)
