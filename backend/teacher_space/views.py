from typing import Self
from django.shortcuts import render, redirect
from django.http import FileResponse
from django.conf import settings
import os
from PyPDF2 import PdfReader
import json

from rest_framework.decorators import (
    api_view, 
    permission_classes, 
    parser_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status

from .models import Module, PDF, Quiz, Question, Choix
from .serializers import (
    ModuleSerializer,
    PDFSerializer,
    QuizSerializer,
    QuizDetailSerializer,
    QuizListSerializer,
    GeneratedQuizSerializer,
    QuestionSerializer
)
from .services.gemini_service import GeminiService

# Vue de redirection après login
def after_login_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.role == 'teacher':
        if Module.objects.filter(teacher=request.user).exists():
            return redirect('/teacher/modules')
        return redirect('/teacher-create-module')
    elif request.user.role == 'student':
        return redirect('student_dashboard')
    elif request.user.role == 'admin':
        return redirect('admin_dashboard')
    return redirect('login')

# Vues pour les modules
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_teacher_modules(request):
    if request.user.role != 'teacher':
        return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)
    return Response({
        'has_modules': Module.objects.filter(teacher=request.user).exists()
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_module(request):
    if request.user.role != 'teacher':
        return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

    name = request.data.get('name')
    if not name:
        return Response({'error': 'Module name is required'}, status=status.HTTP_400_BAD_REQUEST)

    module = Module.objects.create(name=name, teacher=request.user)
    return Response(ModuleSerializer(module).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_modules(request):
    if request.user.role != 'teacher':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    modules = Module.objects.filter(teacher=request.user)
    return Response(ModuleSerializer(modules, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def module_detail(request, pk):
    try:
        module = Module.objects.get(id=pk, teacher=request.user)
        return Response(ModuleSerializer(module).data)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)

# Vues pour les PDFs
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_pdfs(request, module_id):
    try:
        module = Module.objects.get(id=module_id, teacher=request.user)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)

    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    pdf = PDF.objects.create(
        titre=request.FILES['file'].name,
        fichier=request.FILES['file'],
        module=module
    )
    return Response(PDFSerializer(pdf).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def module_pdfs(request, module_id):
    try:
        module = Module.objects.get(id=module_id, teacher=request.user)
        pdfs = PDF.objects.filter(module=module)
        
        pdfs_data = [{
            'id': pdf.id,
            'name': pdf.titre,
            'url': request.build_absolute_uri(pdf.fichier.url),
            'headers': {'X-Frame-Options': 'ALLOW-FROM http://localhost:3000'}
        } for pdf in pdfs]
            
        return Response(pdfs_data)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_pdf(request, module_id, pdf_id):
    try:
        pdf = PDF.objects.get(id=pdf_id, module__id=module_id, module__teacher=request.user)
        pdf.fichier.delete()
        pdf.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except PDF.DoesNotExist:
        return Response({'error': 'PDF not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_protected_pdf(request, pdf_id):
    try:
        pdf = PDF.objects.get(id=pdf_id, module__teacher=request.user)
        file_path = os.path.join(settings.MEDIA_ROOT, str(pdf.fichier))
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['X-Frame-Options'] = 'ALLOW-FROM http://localhost:3000'
        return response
    except PDF.DoesNotExist:
        return Response({'error': 'PDF not found'}, status=status.HTTP_404_NOT_FOUND)

# Vues pour les quiz
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quiz(request):
    if request.user.role != 'teacher':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    titre = request.data.get('titre')
    module_id = request.data.get('module')
    
    if not titre or not module_id:
        return Response({'error': 'Title and module are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        module = Module.objects.get(id=module_id, teacher=request.user)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found or not yours'}, status=status.HTTP_404_NOT_FOUND)

    quiz = Quiz.objects.create(
        titre=titre,
        description=request.data.get('description', ''),
        module=module
    )
    return Response(QuizSerializer(quiz).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_module_quizzes(request, module_id):
    try:
        module = Module.objects.get(id=module_id, teacher=request.user)
        quizzes = Quiz.objects.filter(module=module)
        return Response(QuizSerializer(quizzes, many=True).data)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def module_quizzes(request, module_id):
    try:
        module = Module.objects.get(id=module_id, teacher=request.user)
        quizzes = Quiz.objects.filter(module=module).order_by('-date_creation')
        return Response(QuizListSerializer(quizzes, many=True).data)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_detail(request, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id, module__teacher=request.user)
        return Response(QuizDetailSerializer(quiz).data)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found or not yours'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id, module__teacher=request.user)
        
        # Mise à jour des champs de base
        quiz.titre = request.data.get('title', quiz.titre)
        quiz.description = request.data.get('description', quiz.description)
        quiz.save()

        # Mise à jour des questions
        for question_data in request.data.get('questions', []):
            Self._update_or_create_question(quiz, question_data)

        return Response(QuizSerializer(quiz).data)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found or not yours'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def _update_or_create_question(self, quiz, question_data):
    question_id = question_data.get('id')
    if question_id:
        question = Question.objects.get(id=question_id, quiz=quiz)
        question.enonce = question_data.get('text', question.enonce)
        question.save()
    else:
        question = Question.objects.create(
            quiz=quiz,
            enonce=question_data.get('text', '')
        )

    # Mise à jour des choix
    for choice_data in question_data.get('choices', []):
        self._update_or_create_choice(question, choice_data)

def _update_or_create_choice(self, question, choice_data):
    choice_id = choice_data.get('id')
    if choice_id:
        choix = Choix.objects.get(id=choice_id)
        choix.texte = choice_data.get('text', '')
        choix.is_correct = choice_data.get('is_correct', False)
        choix.save()
    else:
        Choix.objects.create(
            question=question,
            texte=choice_data.get('text', ''),
            is_correct=choice_data.get('is_correct', False)
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id, module__teacher=request.user)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found or not yours'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id, quiz__module__teacher=request.user)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Question.DoesNotExist:
        return Response({'error': 'Question not found or not yours'}, status=status.HTTP_404_NOT_FOUND)

# Vue pour générer un quiz avec Gemini
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_quiz(request, module_id):
    if request.user.role != 'teacher':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    try:
        module = Module.objects.get(id=module_id, teacher=request.user)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found or not yours'}, status=status.HTTP_404_NOT_FOUND)

    # Vérification PDF
    pdfs = PDF.objects.filter(module=module)
    if not pdfs.exists():
        return Response({'error': 'No PDF uploaded for this module'}, status=status.HTTP_400_BAD_REQUEST)

    # Extraction texte
    try:
        latest_pdf = pdfs.order_by('-date_upload').first()
        full_text = Self._extract_text_from_pdf(latest_pdf.fichier)
    except Exception as e:
        return Response({'error': f'Could not extract text from PDF: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    # Génération quiz
    try:
        gemini = GeminiService()
        quiz_data = gemini.generate_quiz_from_text(full_text)
        
        if not quiz_data or 'questions' not in quiz_data:
            return Response({'error': 'Invalid response from Gemini'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Self._save_generated_quiz(module, quiz_data)
    except Exception as e:
        return Response({'error': f'Gemini service error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _extract_text_from_pdf(self, pdf_file):
    full_text = ""
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + "\n"
    return full_text

def _save_generated_quiz(self, module, quiz_data):
    quiz = Quiz.objects.create(
        module=module,
        titre=quiz_data.get('title', f'Quiz pour {module.name}')[:100],
        description=quiz_data.get('description', '')[:500],
        is_generated=True
    )

    questions = []
    for q in quiz_data['questions']:
        question = Question.objects.create(
            quiz=quiz,
            enonce=q['question'][:500]
        )
        
        choices = []
        for i, option in enumerate(q['options'][:4]):
            is_correct = (i == q['correct_answer'])
            choice = Choix.objects.create(
                question=question,
                texte=option[:200],
                is_correct=is_correct
            )
            choices.append({
                'id': choice.id,
                'text': choice.texte,
                'is_correct': choice.is_correct
            })
        
        questions.append({
            'id': question.id,
            'text': question.enonce,
            'choices': choices,
            'correct_answer': q['correct_answer']
        })

    return Response({
        'id': quiz.id,
        'title': quiz.titre,
        'description': quiz.description,
        'is_generated': True,
        'questions': questions
    }, status=status.HTTP_201_CREATED)

# Vues utilitaires
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_pdf_uploaded(request, module_id):
    try:
        module = Module.objects.get(id=module_id, teacher=request.user)
        return Response({'has_pdf': PDF.objects.filter(module=module).exists()})
    except Module.DoesNotExist:
        return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_pdf(request, module_id):
    try:
        module = Module.objects.get(id=module_id, teacher=request.user)
        pdf = PDF.objects.filter(module=module).order_by('-date_upload').first()
        if pdf:
            return Response({
                'id': pdf.id,
                'name': pdf.titre,
                'url': request.build_absolute_uri(pdf.fichier.url)
            })
        return Response({'error': 'No PDF found'}, status=status.HTTP_404_NOT_FOUND)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_generated_quiz(request, module_id):
    try:
        module = Module.objects.get(id=module_id, teacher=request.user)
        quiz = Quiz.objects.filter(module=module, is_generated=True).order_by('-date_creation').first()
        if not quiz:
            return Response({'error': 'No generated quiz found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(GeneratedQuizSerializer(quiz).data)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)