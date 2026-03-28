"""
=====================================================================
📄 CV OPTIMIZER - ADAPTATION DU CV À UNE OFFRE D'EMPLOI
=====================================================================

🎯 RÔLE :
Adapter le CV pour mieux correspondre aux exigences d'une offre d'emploi.

📚 ALGORITHME :
1. Analyser l'offre pour extraire les compétences clés
2. Comparer avec le CV original
3. Mettre en avant les compétences correspondantes
4. Ajouter des mots-clés pertinents
5. Générer une version optimisée du CV
=====================================================================
"""

import os
import re
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def optimize_cv_for_job(
    cv_text: str, 
    job_title: str, 
    job_description: str, 
    missing_skills: List[str],
    strengths: List[str]
) -> str:
    """
    Optimise le CV pour correspondre à une offre d'emploi spécifique.
    
    Args:
        cv_text: Texte original du CV
        job_title: Titre du poste
        job_description: Description de l'offre
        missing_skills: Compétences manquantes identifiées
        strengths: Points forts du candidat
    
    Returns:
        CV optimisé au format texte
    """
    
    try:
        # Construction du prompt pour l'IA
        prompt = f"""
Tu es un expert en optimisation de CV.

Voici le CV original du candidat :
---
{cv_text[:3000]}
---

Voici l'offre d'emploi :
**Titre :** {job_title}
**Description :** {job_description[:2000]}

**Points forts du candidat :** {', '.join(strengths) if strengths else 'Non spécifiés'}

**Compétences à mettre en avant :** {', '.join(missing_skills) if missing_skills else 'Aucune'}

OBJECTIF :
Génère une version optimisée du CV qui :
1. Met en avant les compétences qui correspondent à l'offre
2. Reformule l'expérience pour utiliser les mots-clés de l'offre
3. Ajoute une section "Compétences clés" avec les compétences pertinentes
4. Garde la structure professionnelle d'un CV

RÈGLES :
- Conserve toutes les informations réelles du candidat (ne pas inventer)
- Utilise un ton professionnel
- Structure claire : Coordonnées, Résumé, Compétences, Expériences, Formation
- Longueur maximale : 2 pages

Génère le CV optimisé au format texte.
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en recrutement et en optimisation de CV. Tu génères des CV professionnels et percutants."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        optimized_cv = response.choices[0].message.content
        
        return optimized_cv
        
    except Exception as e:
        print(f"❌ Erreur lors de l'optimisation du CV : {e}")
        return cv_text  # Retourne le CV original en cas d'erreur


def create_cv_highlights(missing_skills: List[str], strengths: List[str]) -> str:
    """
    Crée une section "Points forts" pour le CV basée sur l'offre.
    """
    highlights = []
    
    if strengths:
        highlights.append("🎯 Points forts :")
        for s in strengths[:5]:
            highlights.append(f"  • {s}")
    
    if missing_skills:
        highlights.append("\n💪 Compétences développées :")
        for s in missing_skills[:5]:
            highlights.append(f"  • {s} (en cours de renforcement)")
    
    return "\n".join(highlights) if highlights else ""