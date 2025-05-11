from rest_framework import serializers
from .models import PDF, Module, Choix, Quiz, Question
from .models import StudentProgress, StudentQuizAttempt, StudentAnswer

class ModuleSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    class Meta:
        model = Module
        fields = ['id', 'name', 'student', 'created_at']

class PDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDF
        fields = ['id', 'module', 'titre', 'fichier', 'date_upload']
        read_only_fields = ['titre', 'date_upload']

class ChoixSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choix
        fields = ['id', 'texte', 'is_correct']


#########################################
class StudentQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'titre', 'description', 'date_creation']

class StudentQuizDetailSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'titre', 'description', 'date_creation', 'questions']

    def get_questions(self, obj):
        questions = Question.objects.filter(quiz=obj)
        return [{
            'id': q.id,
            'enonce': q.enonce,
            'choix': [{
                'id': c.id,
                'texte': c.texte
            } for c in q.choix.all()]
        } for q in questions]

class StudentAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.titre', read_only=True)
    
    class Meta:
        model = StudentQuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'start_time', 'end_time', 'score']

class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ['id', 'attempt', 'question', 'choice', 'answered_at']