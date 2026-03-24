# ==========================================================
# 🧠 AI AGENT SERVICE (CORE IA)
# ==========================================================
# 🎯 RÔLE :
# Centraliser TOUTES les interactions avec OpenAI
#
# 👉 Fournit :
# - analyse CV
# - analyse offre
# - matching CV / job
# - scoring avancé
# - optimisation CV
# - génération candidature
#
# 🔥 C’est le cerveau IA de ton application
#
# ==========================================================


# ==========================================================
# 🔹 IMPORTS
# ==========================================================
import json
import re
from typing import Dict, Any

from openai import OpenAI
from app.core.config import settings


# ==========================================================
# 🔹 CLIENT OPENAI (GLOBAL)
# ==========================================================
# 👉 IMPORTANT :
# Un seul client pour toute l'application
# évite bugs + optimise performances

client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ==========================================================
# 🔹 LOW LEVEL CALL IA
# ==========================================================
def ask_ai(system_prompt: str, user_prompt: str, temperature: float | None = None) -> str:
    """
    🔥 FONCTION CENTRALE

    👉 Envoie une requête à OpenAI
    👉 Retourne du texte brut

    UTILISATION :
    toutes les fonctions passent par ici
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
# 🔹 PARSE JSON ROBUSTE
# ==========================================================
def parse_json_response(text: str) -> Dict[str, Any]:
    """
    🔥 CRITIQUE

    👉 GPT ne respecte pas toujours le JSON
    👉 on nettoie + sécurise

    Gère :
    - ```json
    - texte autour
    - erreurs
    """

    try:
        text = text.strip()

        # enlever ```json
        if text.startswith("```"):
            parts = text.split("```")
            text = parts[1] if len(parts) > 1 else text

            if text.startswith("json"):
                text = text[4:]

        # extraction JSON via regex
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            return {
                "error": "No JSON found",
                "raw": text
            }

        return json.loads(match.group())

    except Exception as e:
        return {
            "error": "Parsing failed",
            "raw": text,
            "details": str(e)
        }


# ==========================================================
# 🔹 WRAPPER JSON
# ==========================================================
def ask_ai_json(system_prompt: str, user_prompt: str, temperature: float | None = None) -> Dict[str, Any]:
    """
    🔥 VERSION SAFE

    👉 appelle l'IA
    👉 parse automatiquement le JSON
    """

    raw = ask_ai(system_prompt, user_prompt, temperature)
    return parse_json_response(raw)


# ==========================================================
# 🔹 CLEAN CV TEXT
# ==========================================================
def clean_cv_text(raw_text: str) -> str:
    """
    Nettoie le texte brut d’un CV

    👉 Évite bugs IA
    👉 améliore compréhension
    """

    if not raw_text:
        return ""

    # caractères invisibles
    cleaned = re.sub(r"[\x00-\x09\x0b-\x1f\x7f]", " ", raw_text)

    # normalisation
    cleaned = cleaned.replace("\r", "\n")
    cleaned = cleaned.replace("\\", "")

    # espaces multiples
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


# ==========================================================
# 🔹 ANALYSE OFFRE
# ==========================================================
def analyze_offer(offer: Any) -> Dict[str, Any]:
    """
    Analyse une offre d'emploi

    👉 transforme texte brut → structure exploitable
    👉 utilisé par :
        job_search
        matching
    """

    system_prompt = "Tu es un expert en analyse RH."

    user_prompt = f"""
Analyse cette offre :

Titre : {getattr(offer, 'title', '')}
Description : {getattr(offer, 'description', '')}

FORMAT STRICT :

{{
  "analysis": {{
    "resume": "",
    "hard_skills": [],
    "soft_skills": [],
    "experience_level": "",
    "keywords": []
  }}
}}
"""

    return ask_ai_json(system_prompt, user_prompt, temperature=0.2)


# ==========================================================
# 🔹 ANALYSE CV
# ==========================================================
def analyze_cv(cv_text: str) -> Dict[str, Any]:
    """
    Analyse un CV

    👉 CV → profil structuré
    """

    system_prompt = "Tu es un expert en analyse de CV."

    user_prompt = f"""
Analyse ce CV :

CV :
{cv_text}

FORMAT STRICT :

{{
  "analysis": {{
    "resume": "",
    "hard_skills": [],
    "soft_skills": [],
    "experience_level": "",
    "keywords": []
  }}
}}
"""

    return ask_ai_json(system_prompt, user_prompt, temperature=0.2)


# ==========================================================
# 🔹 MATCHING CV / OFFRE
# ==========================================================
def match_cv_offer(cv_analysis: Dict[str, Any], offer_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare CV vs Offre

    👉 produit un score + insights
    """

    system_prompt = "Tu es expert matching RH."

    user_prompt = f"""
Compare :

CV :
{json.dumps(cv_analysis)}

OFFRE :
{json.dumps(offer_analysis)}

FORMAT :

{{
  "match": {{
    "matching_score": 0,
    "missing_skills": [],
    "strengths": [],
    "summary": ""
  }}
}}
"""

    return ask_ai_json(system_prompt, user_prompt)


# ==========================================================
# 🔹 SCORING AVANCÉ
# ==========================================================
def score_analysis(cv_analysis: Dict[str, Any], offer_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score détaillé

    👉 utile pour dashboard
    """

    system_prompt = "Tu es expert scoring RH."

    user_prompt = f"""
Compare :

CV :
{json.dumps(cv_analysis)}

OFFRE :
{json.dumps(offer_analysis)}

FORMAT :

{{
  "score": {{
    "global_score": 0,
    "technical_score": 0,
    "experience_score": 0,
    "summary": ""
  }}
}}
"""

    return ask_ai_json(system_prompt, user_prompt)


# ==========================================================
# 🔹 OPTIMISATION CV
# ==========================================================
def optimize_cv_for_offer(cv_analysis, offer_analysis, match_result):
    """
    Génère un CV optimisé

    👉 améliore matching ATS
    """

    system_prompt = "Tu es expert optimisation CV."

    user_prompt = f"""
Optimise ce CV :

CV :
{json.dumps(cv_analysis)}

OFFRE :
{json.dumps(offer_analysis)}

MATCH :
{json.dumps(match_result)}

FORMAT :

{{
  "optimized_cv": {{
    "summary": "",
    "skills": [],
    "experience": []
  }}
}}
"""

    return ask_ai_json(system_prompt, user_prompt)


# ==========================================================
# 🔹 AUTO APPLY (FULL PIPELINE IA)
# ==========================================================
def auto_apply(cv_text: str, offer: Dict[str, Any]):
    """
    🔥 MODE FULL AUTOMATIQUE

    👉 génère directement :
    - lettre de motivation
    """

    system_prompt = "Tu es assistant RH autonome."

    user_prompt = f"""
CV :
{cv_text}

OFFRE :
{json.dumps(offer)}

FORMAT :

{{
  "auto_apply": {{
    "cover_letter": ""
  }}
}}
"""

    return ask_ai_json(system_prompt, user_prompt, temperature=0.3)