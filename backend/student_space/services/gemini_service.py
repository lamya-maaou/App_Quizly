import google.generativeai as genai
import json
import re
from typing import Dict, Optional
from django.conf import settings

class StudentGeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            'gemini-1.5-pro-latest',
            generation_config={
                'temperature': 0.5,  # Un peu plus bas pour des explications précises
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 2000
            }
        )

    def get_explanation_for_question(self, question_text: str, student_answer: str, correct_answer: str) -> Optional[Dict]:
        """
        Génère une explication pédagogique pour une question de quiz
        
        Args:
            question_text: Texte de la question
            student_answer: Réponse choisie par l'étudiant
            correct_answer: Bonne réponse
            
        Returns:
            Un dictionnaire avec l'explication ou None si erreur
        """
        prompt = f"""Tu es un tuteur pédagogique. Fournis une explication claire et bienveillante pour cette question de quiz.

Question: {question_text}

Réponse étudiante: {student_answer}
Bonne réponse: {correct_answer}

Génère une réponse JSON avec cette structure:
{{
  "is_correct": true|false,
  "explanation": "Explication détaillée de pourquoi la réponse est correcte/incorrecte",
  "hints": ["Indice 1", "Indice 2"]  // 2 indices pour mieux comprendre
}}

Règles:
- Sois encourageant même si la réponse est fausse
- Fournis des explications conceptuelles, pas juste la réponse
- Les indices doivent aider à comprendre sans donner la réponse directement
- Maximum 3 phrases pour l'explication principale
"""
        try:
            response = self.model.generate_content(prompt)
            explanation_data = self._parse_response(response.text)
            return explanation_data
        except Exception as e:
            print(f"Erreur Gemini: {str(e)}")
            return None

    def generate_study_tips(self, weak_areas: list) -> Optional[Dict]:
        """
        Génère des conseils d'étude personnalisés
        
        Args:
            weak_areas: Liste des thèmes où l'étudiant a des difficultés
            
        Returns:
            Un plan d'étude structuré ou None si erreur
        """
        prompt = f"""Crée un plan d'étude personnalisé pour un étudiant ayant des difficultés dans:
{', '.join(weak_areas)}

Structure REQUISE:
{{
  "plan_title": "Titre du plan",
  "weekly_schedule": [
    {{
      "week": 1,
      "topics": ["Sujet1", "Sujet2"],
      "activities": ["Activité1", "Activité2"],
      "resources": ["Type de ressource recommandée"]
    }}
  ],
  "general_advice": ["Conseil1", "Conseil2"]
}}

Règles:
- Plan sur 4 semaines maximum
- Activités concrètes et réalisables
- Mélange de théorie et pratique
- Adapté à des apprenants universitaires
"""
        try:
            response = self.model.generate_content(prompt)
            study_plan = self._parse_response(response.text)
            return study_plan
        except Exception as e:
            print(f"Erreur Gemini: {str(e)}")
            return None

    def _parse_response(self, response_text: str) -> Dict:
        """Nettoyage et extraction du JSON de la réponse"""
        cleaned = re.sub(r'^```(json)?|```$', '', response_text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r'//.*?$', '', cleaned, flags=re.MULTILINE)
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError("Réponse JSON invalide")