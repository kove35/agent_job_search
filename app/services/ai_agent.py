# ==========================================================
# IMPORTS
# ==========================================================

# json permet de transformer une chaîne JSON en dictionnaire Python
import json

# re permet de nettoyer du texte avec des expressions régulières
import re

# typing améliore la lisibilité des types
from typing import Dict, Any

# fitz = PyMuPDF pour lire le texte d'un PDF
import fitz

# SDK OpenAI
from openai import OpenAI

# Configuration centralisée du projet
from app.core.config import settings


# ==========================================================
# CLIENT OPENAI
# ==========================================================

# On crée une seule fois le client OpenAI
# Il utilisera la clé définie dans config.py
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ==========================================================
# FONCTION BASSE-NIVEAU : APPEL GÉNÉRIQUE À L'IA
# ==========================================================
def ask_ai(system_prompt: str, user_prompt: str, temperature: float | None = None) -> str:
    """
    Envoie une consigne au modèle OpenAI et renvoie la réponse texte.

    Rôle dans le flux :
    Toutes les fonctions métier de ce fichier passent par cette fonction.
    C'est le point central d'appel à l'IA.
    """

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature if temperature is not None else settings.TEMPERATURE,
        max_tokens=settings.MAX_TOKENS,
    )

    return response.choices[0].message.content.strip()


# ==========================================================
# FONCTION : CONVERTIR UNE RÉPONSE JSON TEXTE EN DICTIONNAIRE
# ==========================================================
def parse_json_response(text: str) -> Dict[str, Any]:
    """
    Essaie de convertir une réponse texte du modèle en vrai JSON Python.

    Si le modèle renvoie un JSON invalide,
    on renvoie un dictionnaire d'erreur au lieu de faire planter le projet.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "error": "Réponse JSON invalide",
            "raw_response": text
        }


# ==========================================================
# FONCTION : APPEL IA QUI ATTEND DU JSON
# ==========================================================
def ask_ai_json(system_prompt: str, user_prompt: str, temperature: float | None = None) -> Dict[str, Any]:
    """
    Fonction pratique :
    - appelle l'IA
    - récupère le texte
    - le convertit en dictionnaire JSON
    """
    raw_text = ask_ai(system_prompt, user_prompt, temperature=temperature)
    return parse_json_response(raw_text)


# ==========================================================
# FONCTION : NETTOYAGE DU TEXTE CV
# ==========================================================
def clean_cv_text(raw_text: str) -> str:
    """
    Nettoie automatiquement un CV brut :
    - supprime les caractères de contrôle
    - normalise les retours à la ligne
    - supprime les backslashes inutiles
    - réduit les espaces multiples

    Rôle dans le flux :
    Cette étape doit être faite juste après l'extraction PDF
    et avant l'analyse du CV.
    """

    if not raw_text:
        return ""

    # Supprimer les caractères de contrôle invisibles
    cleaned = re.sub(r"[\x00-\x09\x0b-\x1f\x7f]", " ", raw_text)

    # Remplacer les retours chariot Windows
    cleaned = cleaned.replace("\r", "\n")

    # Supprimer les backslashes isolés
    cleaned = cleaned.replace("\\", "")

    # Réduire les espaces multiples
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


# ==========================================================
# FONCTION : EXTRACTION TEXTE PDF
# ==========================================================
def cv_to_json(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Lit un PDF reçu sous forme binaire et renvoie son texte.

    Rôle dans le flux :
    Sert à transformer un CV PDF en texte exploitable par l'IA.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""

        for page in doc:
            text += page.get_text()

        return {"text": text}

    except Exception as e:
        return {"error": str(e)}


# ==========================================================
# FONCTION : ANALYSE D'OFFRE
# ==========================================================
def analyze_offer(offer: Any) -> Dict[str, Any]:
    """
    Analyse une offre d'emploi et renvoie une structure JSON.

    Rôle dans le flux :
    Transforme une offre brute ou normalisée en besoin RH structuré.
    Cela servira ensuite au matching.
    """

    system_prompt = "Tu es un expert en analyse RH et recrutement."

    user_prompt = f"""
Tu es un expert en analyse d'offres d'emploi.
Analyse l'offre suivante et renvoie un JSON STRICTEMENT brut.

OFFRE :
Titre : {getattr(offer, 'title', '')}
Description : {getattr(offer, 'description', '')}
Lieu : {getattr(offer, 'location', '')}

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
  "matching_score": 0,
  "recommendations": ["conseil 1", "conseil 2", "conseil 3"]
}}

Règles importantes :
- Renvoie UNIQUEMENT du JSON brut
- Ne laisse jamais une liste vide
- Pas de texte avant ou après
"""

    return ask_ai_json(system_prompt, user_prompt, temperature=0.2)


# ==========================================================
# FONCTION : ANALYSE DE CV
# ==========================================================
def analyze_cv(cv_text: str) -> Dict[str, Any]:
    """
    Analyse un CV texte et renvoie une structure JSON.

    Rôle dans le flux :
    Transforme le CV en profil candidat structuré.
    """
    system_prompt = "Tu es un expert en analyse de CV techniques."

    user_prompt = f"""
Tu es un expert en analyse de CV techniques (production, supervision, data, industrie).
Analyse le CV suivant et renvoie un JSON STRICTEMENT brut.

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
- Renvoie UNIQUEMENT du JSON brut
- Ne laisse jamais une liste vide
- Pas de texte avant ou après
"""

    return ask_ai_json(system_prompt, user_prompt, temperature=0.2)


# ==========================================================
# FONCTION : MATCHING CV / OFFRE
# ==========================================================
def match_cv_offer(cv_analysis: Dict[str, Any], offer_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare l'analyse du CV et l'analyse de l'offre.

    Rôle dans le flux :
    C'est ici qu'on décide si le candidat doit postuler ou non.
    """
    system_prompt = "Tu es un expert en matching RH et analyse de compatibilité."

    user_prompt = f"""
Tu es un expert en matching RH.
Compare l'analyse du CV et l'analyse de l'offre ci-dessous.

CV :
{json.dumps(cv_analysis, ensure_ascii=False)}

OFFRE :
{json.dumps(offer_analysis, ensure_ascii=False)}

Renvoie un JSON STRICTEMENT brut au format suivant :

{{
  "matching_score": 0,
  "missing_skills": ["compétence manquante 1", "compétence manquante 2"],
  "strengths": ["point fort 1", "point fort 2"],
  "summary": "Résumé clair du matching en 3-4 lignes"
}}

Règles :
- Renvoie uniquement du JSON brut
- Pas de texte avant ou après
"""

    return ask_ai_json(system_prompt, user_prompt, temperature=0.2)


# ==========================================================
# FONCTION : SCORING AVANCÉ
# ==========================================================
def score_analysis(cv_analysis: Dict[str, Any], offer_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Génère un score détaillé entre CV et offre.

    Rôle dans le flux :
    Produit un score exploitable dans le dashboard
    et pour la décision automatique.
    """
    system_prompt = "Tu es un expert en scoring RH."

    user_prompt = f"""
Tu es un expert en scoring RH.
Compare ces deux analyses et génère un score détaillé.

CV :
{json.dumps(cv_analysis, ensure_ascii=False)}

OFFRE :
{json.dumps(offer_analysis, ensure_ascii=False)}

Renvoie un JSON STRICTEMENT brut :

{{
  "global_score": 0,
  "technical_score": 0,
  "soft_skills_score": 0,
  "experience_score": 0,
  "keywords_match": ["mot1", "mot2"],
  "missing_keywords": ["mot1", "mot2"],
  "summary": "Résumé clair"
}}

Règles :
- Renvoie uniquement du JSON brut
- Pas de texte avant ou après
"""

    return ask_ai_json(system_prompt, user_prompt, temperature=0.2)


# ==========================================================
# FONCTION : OPTIMISATION DE CV POUR UNE OFFRE
# ==========================================================
def optimize_cv_for_offer(
    cv_analysis: Dict[str, Any],
    offer_analysis: Dict[str, Any],
    match_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Génère une version optimisée du CV pour mieux coller à l'offre.

    Rôle dans le flux :
    Sert à produire une candidature plus ciblée.
    """
    system_prompt = "Tu es un expert en optimisation de CV et matching RH."

    user_prompt = f"""
Tu es un expert en optimisation de CV pour augmenter le matching avec une offre d'emploi.

Voici l'analyse du CV :
{json.dumps(cv_analysis, ensure_ascii=False)}

Voici l'analyse de l'offre :
{json.dumps(offer_analysis, ensure_ascii=False)}

Voici le résultat du matching :
{json.dumps(match_result, ensure_ascii=False)}

Ta mission :
- Générer une version optimisée du CV du candidat
- Mettre en avant les compétences pertinentes pour l'offre
- Ajouter les compétences manquantes si elles sont cohérentes
- Renforcer les points forts
- Reformuler les expériences pour coller à l'offre

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
- Renvoie uniquement du JSON brut
- Pas de texte avant ou après
"""

    return ask_ai_json(system_prompt, user_prompt, temperature=0.2)


# ==========================================================
# FONCTION : PIPELINE COMPLET AUTO_APPLY
# ==========================================================
def auto_apply(cv_text: str, offer: Dict[str, Any]) -> Dict[str, Any]:
    """
    Demande au modèle de faire tout le travail d'un seul coup.

    Rôle dans le flux :
    Fonction pratique pour prototyper rapidement,
    mais moins contrôlable que le pipeline étape par étape.
    """
    system_prompt = "Tu es un assistant RH autonome spécialisé en optimisation de candidatures."

    user_prompt = f"""
Tu es un assistant RH autonome. À partir du CV et de l'offre, génère :

1. Analyse du CV
2. Analyse de l'offre
3. Matching
4. CV optimisé
5. Lettre de motivation optimisée

CV :
{cv_text}

OFFRE :
{json.dumps(offer, ensure_ascii=False)}

Renvoie un JSON STRICTEMENT brut :

{{
  "cv_analysis": {{...}},
  "offer_analysis": {{...}},
  "match": {{...}},
  "optimized_cv": {{...}},
  "cover_letter": "texte"
}}

Règles :
- Renvoie uniquement du JSON brut
- Pas de texte avant ou après
"""

    return ask_ai_json(system_prompt, user_prompt, temperature=0.3)