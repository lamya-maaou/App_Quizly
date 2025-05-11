

from django.db import models
from auth_app.models import CustomUser


# Create your models here.
class Module(models.Model):
    name = models.CharField(max_length=100)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='student_modules')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class PDF(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="pdfs")
    titre = models.CharField(max_length=100)
    fichier = models.FileField(upload_to="pdfs/")
    date_upload = models.DateTimeField(auto_now_add=True)


class Quiz(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="quizzes")
    titre = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    is_generated = models.BooleanField(default=False)
    
    def __str__(self):
        return self.titre
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    enonce = models.TextField()
    bonnes_reponses = models.ManyToManyField("Choix", related_name="questions_ou_je_suis_bonne_reponse")


# Choix de la reponse
class Choix(models.Model):
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="choix")
    texte = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.texte
    

    #########################################
class StudentProgress(models.Model):
    """Suivi de la progression de l'étudiant"""
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'module')

class StudentQuizAttempt(models.Model):
    """Tentative de quiz par un étudiant"""
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)

    def calculate_score(self):
        # Logique de calcul du score
        correct_answers = self.answers.filter(choice__is_correct=True).count()
        total_questions = self.quiz.questions.count()
        return (correct_answers / total_questions) * 100 if total_questions else 0

class StudentAnswer(models.Model):
    """Réponse d'un étudiant à une question"""
    attempt = models.ForeignKey(StudentQuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey('teacher_space.Choix', on_delete=models.CASCADE)  # Référence à Choix dans teacher_space
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('attempt', 'question')  # Un seul réponse par question par tentative