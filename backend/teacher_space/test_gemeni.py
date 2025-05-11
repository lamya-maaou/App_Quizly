import os
import sys
import django
import json

# Configurez le chemin Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from teacher_space.services.gemini_service import GeminiService

def test_gemini_service():
    print("\n=== Test du service Gemini ===")
    
    # 1. Test avec un texte simple
    test_text = """
    Les mitochondries sont des organites cellulaires responsables de la production d'énergie.
    Elles possèdent leur propre ADN et se reproduisent indépendamment de la cellule.
    On les appelle souvent les 'centrales énergétiques' de la cellule.
    """
    
    print("\nTest 1: Texte simple")
    run_test(test_text)
    
    # 2. Test avec un texte plus long (similaire à un PDF)
    with open(os.path.join(os.path.dirname(__file__), 'test_text.txt'), 'r', encoding='utf-8') as f:
        pdf_like_text = f.read()
    
    print("\nTest 2: Texte type PDF")
    run_test(pdf_like_text[:5000])  # Limité à 5000 caractères pour le test

def run_test(text):
    gemini = GeminiService()
    print(f"\nTexte d'entrée ({len(text)} caractères):")
    print(text[:200] + "...")  # Affiche un extrait
    
    try:
        print("\nAppel à Gemini...")
        response = gemini.generate_quiz_from_text(text)
        
        if not response:
            print("\nERREUR: Réponse vide")
            return
            
        print("\nRéponse reçue:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        if 'questions' not in response:
            print("\nERREUR: Format invalide - clé 'questions' manquante")
        else:
            print(f"\nSUCCÈS: {len(response['questions'])} questions générées")
            
    except Exception as e:
        print(f"\nERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_service()
    input("\nAppuyez sur Entrée pour quitter...")