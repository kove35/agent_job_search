import os
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
import fitz  # PyMuPDF

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------------------------------------
# ANALYSE D'OFFRE
# ---------------------------------------------------------

def analyze_offer(offer):
    prompt = f"""
Tu es un expert en analyse d'offres d'emploi. Analyse l'offre suivante et renvoie un JSON STRICTEMENT brut (sans ```json```, sans backticks, sans texte autour).

OFFRE :
Titre : {offer.title}
Description : {offer.description}
Lieu : {offer.location}

Réponds au format JSON suivant :

{{
  "resume": "Résumé clair en 3-4 lignes",
  "hard_skills": ["compétences techniques"],
  "soft_skills": ["compétences comportementales"],
  "responsibilities": ["responsabilité 1", "responsabilité 2"],
  "experience_level": "Junior / Intermédiaire / Senior",
  "estimated_years_experience": "Nombre d'années estimé",
  "keywords": ["mots clés ATS"],
  "implicit_technologies": ["technos déduites même si non mentionnées"],
  "matching_score": 0-100,
  "recommendations": ["conseil 1", "conseil 2", "conseil 3"]
}}

Règles importantes :
- Renvoie UNIQUEMENT du JSON brut.
- Si l'offre ne mentionne pas explicitement une information, déduis-la.
- Ne laisse jamais une liste vide.
- Pas de texte avant ou après.
- Pas de ```json``` ou de blocs de code.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en analyse RH et recrutement."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content
        return {"analysis": content}

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------
# ANALYSE DE CV
# ---------------------------------------------------------

def analyze_cv(cv_text: str):
    prompt = f"""
Tu es un expert en analyse de CV techniques (production, supervision, data, industrie).
Analyse le CV suivant et renvoie un JSON STRICTEMENT brut (sans ```json```, sans backticks, sans texte autour).

CV :
{cv_text}

Réponds au format JSON suivant :

{{
  "resume": "Résumé clair du profil en 3-4 lignes",
  "hard_skills": ["compétences techniques"],
  "soft_skills": ["compétences comportementales"],
  "responsibilities": ["responsabilité 1", "responsabilité 2"],
  "experience_level": "Junior / Intermédiaire / Senior",
  "estimated_years_experience": "Nombre d'années estimé",
  "keywords": ["mots clés ATS"],
  "implicit_technologies": ["technos déduites même si non mentionnées"],
  "recommendations": ["conseil 1", "conseil 2", "conseil 3"]
}}

Règles importantes :
- Renvoie UNIQUEMENT du JSON brut.
- Ne laisse jamais une liste vide : remplis toujours avec des éléments pertinents.
- Pas de texte avant ou après.
- Pas de ```json``` ou de blocs de code.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en analyse de CV techniques."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content
        return {"analysis": content}

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------
# MATCHING CV / OFFRE
# ---------------------------------------------------------

def match_cv_offer(cv_analysis: Dict[str, Any], offer_analysis: Dict[str, Any]):
    prompt = f"""
Tu es un expert en matching RH. Compare l'analyse du CV et l'analyse de l'offre ci-dessous.

CV :
{cv_analysis}

OFFRE :
{offer_analysis}

Renvoie un JSON STRICTEMENT brut au format suivant :

{{
  "matching_score": 0-100,
  "missing_skills": ["compétence manquante 1", "compétence manquante 2"],
  "strengths": ["point fort 1", "point fort 2"],
  "summary": "Résumé clair du matching en 3-4 lignes"
}}

Règles :
- Renvoie uniquement du JSON brut.
- Pas de texte avant ou après.
- Pas de ```json``` ou de backticks.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en matching RH et analyse de compatibilité."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content
        return {"match": content}

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------
# OPTIMISATION DE CV POUR UNE OFFRE
# ---------------------------------------------------------

def optimize_cv_for_offer(cv_analysis: Dict[str, Any],
                          offer_analysis: Dict[str, Any],
                          match_result: Dict[str, Any]):
    prompt = f"""
Tu es un expert en optimisation de CV pour augmenter le matching avec une offre d'emploi.

Voici l'analyse du CV :
{cv_analysis}

Voici l'analyse de l'offre :
{offer_analysis}

Voici le résultat du matching :
{match_result}

Ta mission :
- Générer une version optimisée du CV du candidat
- Mettre en avant les compétences pertinentes pour l'offre
- Ajouter les compétences manquantes si elles sont cohérentes (ex : SQL niveau débutant)
- Renforcer les points forts
- Améliorer la communication et la clarté
- Reformuler les expériences pour coller à l'offre
- Garder un style professionnel et concis

Renvoie un JSON STRICTEMENT brut au format suivant :

{{
  "optimized_title": "Titre optimisé du CV",
  "optimized_summary": "Résumé professionnel optimisé",
  "optimized_hard_skills": ["compétence 1", "compétence 2"],
  "optimized_soft_skills": ["compétence 1", "compétence 2"],
  "optimized_experience": {{
      "experience_1": "Texte optimisé",
      "experience_2": "Texte optimisé"
  }},
  "recommendations": ["conseil 1", "conseil 2"]
}}

Règles :
- Renvoie uniquement du JSON brut.
- Pas de texte avant ou après.
- Pas de ```json``` ou de backticks.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en optimisation de CV et matching RH."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content
        return {"optimized_cv": content}

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------
# CONVERSION CV PDF → TEXTE JSON
# ---------------------------------------------------------

def cv_to_json(pdf_bytes: bytes):
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------
# SCORING AVANCÉ
# ---------------------------------------------------------

def score_analysis(cv_analysis: Dict[str, Any], offer_analysis: Dict[str, Any]):
    prompt = f"""
Tu es un expert en scoring RH. Compare ces deux analyses et génère un score détaillé.

CV :
{cv_analysis}

OFFRE :
{offer_analysis}

Renvoie un JSON STRICTEMENT brut :

{{
  "global_score": 0-100,
  "technical_score": 0-100,
  "soft_skills_score": 0-100,
  "experience_score": 0-100,
  "keywords_match": ["mot1", "mot2"],
  "missing_keywords": ["mot1", "mot2"],
  "summary": "Résumé clair"
}}

Règles :
- Renvoie uniquement du JSON brut.
- Pas de texte avant ou après.
- Pas de ```json``` ou de backticks.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en scoring RH."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content
        return {"score": content}

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------
# PIPELINE COMPLET AUTO_APPLY
# ---------------------------------------------------------

def auto_apply(cv_text: str, offer: Dict[str, Any]):
    prompt = f"""
Tu es un assistant RH autonome. À partir du CV et de l'offre, génère :

1. Analyse du CV
2. Analyse de l'offre
3. Matching
4. CV optimisé
5. Lettre de motivation optimisée

CV :
{cv_text}

OFFRE :
{offer}

Renvoie un JSON STRICTEMENT brut :

{{
  "cv_analysis": {{...}},
  "offer_analysis": {{...}},
  "match": {{...}},
  "optimized_cv": {{...}},
  "cover_letter": "texte"
}}

Règles :
- Renvoie uniquement du JSON brut.
- Pas de texte avant ou après.
- Pas de ```json``` ou de backticks.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un assistant RH autonome spécialisé en optimisation de candidatures."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content
        return {"auto_apply": content}

    except Exception as e:
        return {"error": str(e)}

import re

def clean_cv_text(raw_text: str) -> str:
    """
    Nettoie automatiquement un CV brut pour le rendre compatible JSON :
    - supprime les caractères de contrôle
    - normalise les retours à la ligne
    - supprime les backslashes invalides
    - remplace les caractères invisibles
    """
    # Supprimer les caractères de contrôle (hors \n)
    cleaned = re.sub(r"[\x00-\x09\x0b-\x1f\x7f]", " ", raw_text)

    # Normaliser les retours à la ligne
    cleaned = cleaned.replace("\r", "\n")

    # Supprimer les backslashes inutiles
    cleaned = cleaned.replace("\\", "")

    # Nettoyer les espaces multiples
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()
