"""
=====================================================================
🧠 AI AGENT SERVICE (CORE IA) - VERSION COMPLÈTE
=====================================================================

🎯 RÔLE :
Centraliser TOUTES les interactions avec OpenAI

📚 POUR UN DÉBUTANT :
Ce fichier est le "cerveau" de l'application. Toutes les fois où l'IA
est appelée, c'est ici que ça se passe.

=====================================================================
"""

import json
import re
import logging
from typing import Dict, Any, Optional
from functools import lru_cache

from openai import OpenAI, APIError, RateLimitError
from app.core.config import settings

# Configuration du logging
logger = logging.getLogger(__name__)

# Client OpenAI unique
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ==============================================================
# 🔹 LOW LEVEL CALL IA
# ==============================================================

def ask_ai(system_prompt: str, user_prompt: str, temperature: float | None = None) -> str:
    """
    🔥 FONCTION CENTRALE - Envoie une requête à OpenAI

    📚 EXPLICATION :
    C'est la fonction de base qui appelle l'API OpenAI.
    Toutes les autres fonctions passent par ici.

    Args:
        system_prompt: Instructions pour l'IA (son rôle)
        user_prompt: La question/texte à traiter
        temperature: Créativité (0 = précis, 1 = créatif)

    Returns:
        str: La réponse de l'IA
    """

    temp = temperature if temperature is not None else settings.TEMPERATURE

    try:
        logger.info(f"Appel OpenAI - modèle: {settings.OPENAI_MODEL}")

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temp,
            max_tokens=settings.MAX_TOKENS,
        )

        result = response.choices[0].message.content.strip()

        # Log des tokens utilisés
        if hasattr(response, 'usage'):
            logger.info(f"Tokens utilisés: {response.usage.total_tokens}")

        return result

    except RateLimitError as e:
        logger.error(f"Rate limit atteint: {e}")
        raise Exception("Limite d'appels API atteinte. Réessayez plus tard.")
    except APIError as e:
        logger.error(f"Erreur API OpenAI: {e}")
        raise Exception("L'IA est temporairement indisponible.")
    except Exception as e:
        logger.exception(f"Erreur inattendue: {e}")
        raise Exception(f"Erreur lors de l'appel IA: {str(e)}")


# ==============================================================
# 🔹 PARSE JSON ROBUSTE
# ==============================================================

def parse_json_response(text: str) -> Dict[str, Any]:
    """Transforme le texte de l'IA en dictionnaire Python"""

    try:
        text = text.strip()

        # Enlève les blocs ```json ... ```
        if text.startswith("```"):
            parts = text.split("```")
            text = parts[1] if len(parts) > 1 else text
            if text.startswith("json"):
                text = text[4:]

        # Cherche un objet JSON
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {"error": "No JSON found", "raw": text[:200]}

        return json.loads(match.group())

    except Exception as e:
        return {"error": "Parsing failed", "raw": text[:200], "details": str(e)}


def ask_ai_json(system_prompt: str, user_prompt: str, temperature: float | None = None) -> Dict[str, Any]:
    """Appelle l'IA et parse automatiquement le JSON"""
    raw = ask_ai(system_prompt, user_prompt, temperature)
    return parse_json_response(raw)


# ==============================================================
# 🔹 CLEAN CV TEXT
# ==============================================================

def clean_cv_text(raw_text: str) -> str:
    """Nettoie le texte brut d'un CV"""
    if not raw_text:
        return ""

    cleaned = re.sub(r"[\x00-\x09\x0b-\x1f\x7f]", " ", raw_text)
    cleaned = cleaned.replace("\r", "\n")
    cleaned = cleaned.replace("\\", "")
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


# ==============================================================
# 🔹 ANALYSE OFFRE
# ==============================================================

def analyze_offer(offer: Any) -> Dict[str, Any]:
    """Analyse une offre d'emploi"""

    title = getattr(offer, 'title', '')
    description = getattr(offer, 'description', '')

    system_prompt = "Tu es un expert en analyse RH. Réponds uniquement au format JSON."

    user_prompt = f"""
Analyse cette offre d'emploi et retourne un JSON strict.

Titre : {title}
Description : {description[:3000]}

Le JSON doit avoir cette structure EXACTE :
{{
  "analysis": {{
    "resume": "résumé court de l'offre",
    "hard_skills": ["skill1", "skill2"],
    "soft_skills": ["skill1", "skill2"],
    "experience_level": "junior|confirmé|senior",
    "keywords": ["mot1", "mot2"]
  }}
}}
"""

    return ask_ai_json(system_prompt, user_prompt, temperature=0.2)


# ==============================================================
# 🔹 MATCHING CV / OFFRE (AVEC TEXTE)
# ==============================================================

def analyze_offer_with_cv(cv_text: str, job: Any) -> Dict[str, Any]:
    """
    🎯 Analyse la compatibilité entre un CV et une offre d'emploi.
    
    📚 EXPLICATION POUR DÉBUTANT :
    Cette fonction est utilisée par application_builder.py pour générer
    la lettre de motivation. Elle compare le CV (texte brut) avec
    l'offre d'emploi et retourne un score et des listes de compétences.
    
    Args:
        cv_text (str): Le texte extrait du CV (brut)
        job (JobOffer): L'offre d'emploi
    
    Returns:
        dict: {
            "match_score": 75,           # Score de compatibilité (0-100)
            "missing_skills": [...],     # Compétences manquantes
            "strengths": [...]           # Points forts du candidat
        }
    """
    
    system_prompt = """Tu es un expert en recrutement et en analyse de CV.
    Ta mission est d'analyser la compatibilité entre un CV et une offre d'emploi.
    Sois objectif et précis.
    Réponds UNIQUEMENT au format JSON, sans texte additionnel."""

    # Récupérer les informations de l'offre (compatible JobOffer)
    title = getattr(job, 'title', '')
    company = getattr(job, 'company', '')
    location = getattr(job, 'location', '')
    description = getattr(job, 'description', '')
    
    user_prompt = f"""
Analyse la compatibilité entre ce CV et cette offre d'emploi.

=== CV DU CANDIDAT ===
{cv_text[:3000]}

=== OFFRE D'EMPLOI ===
Titre : {title}
Entreprise : {company}
Localisation : {location}
Description :
{description[:1500]}

=== INSTRUCTIONS ===
1. Calcule un score de matching entre 0 et 100 :
   - 0-20 : Très faible compatibilité
   - 21-40 : Faible compatibilité
   - 41-60 : Compatibilité moyenne
   - 61-80 : Bonne compatibilité
   - 81-100 : Excellente compatibilité

2. Identifie les compétences manquantes (maximum 5) :
   - Compétences techniques demandées dans l'offre mais non présentes dans le CV
   - Sois précis (ex: "Python", pas "langage de programmation")

3. Identifie les points forts du candidat (maximum 5) :
   - Compétences du CV qui correspondent à l'offre
   - Expériences pertinentes

=== FORMAT DE RÉPONSE (JSON UNIQUEMENT) ===
{{
    "match_score": 75,
    "missing_skills": ["compétence manquante 1", "compétence manquante 2"],
    "strengths": ["point fort 1", "point fort 2"]
}}
"""

    try:
        result = ask_ai_json(system_prompt, user_prompt, temperature=0.3)
        
        # Nettoyer et valider les résultats
        return {
            "match_score": min(100, max(0, int(result.get("match_score", 0)))),
            "missing_skills": result.get("missing_skills", [])[:5],
            "strengths": result.get("strengths", [])[:5]
        }
        
    except Exception as e:
        logger.error(f"Erreur dans analyze_offer_with_cv : {e}")
        # Valeurs par défaut en cas d'erreur
        return {
            "match_score": 0,
            "missing_skills": [],
            "strengths": []
        }
# ==============================================================
# 🔹 ANALYSE CV
# ==============================================================

def analyze_cv(cv_text: str) -> Dict[str, Any]:
    """Analyse un CV"""

    system_prompt = "Tu es un expert en analyse de CV. Réponds uniquement au format JSON."
    cleaned_cv = clean_cv_text(cv_text)

    user_prompt = f"""
Analyse ce CV et retourne un JSON strict.

CV :
{cleaned_cv[:4000]}

Le JSON doit avoir cette structure EXACTE :
{{
  "analysis": {{
    "resume": "résumé du profil",
    "hard_skills": ["skill1", "skill2"],
    "soft_skills": ["skill1", "skill2"],
    "experience_level": "junior|confirmé|senior",
    "keywords": ["mot1", "mot2"]
  }}
}}
"""

    return ask_ai_json(system_prompt, user_prompt, temperature=0.2)


# ==============================================================
# 🔹 MATCHING CV / OFFRE
# ==============================================================

def match_cv_offer(cv_analysis: Dict[str, Any], offer_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Compare CV et offre pour donner un score"""

    system_prompt = "Tu es expert en matching RH. Réponds uniquement au format JSON."

    user_prompt = f"""
Compare ce CV et cette offre d'emploi.

ANALYSE CV :
{json.dumps(cv_analysis, indent=2, ensure_ascii=False)}

ANALYSE OFFRE :
{json.dumps(offer_analysis, indent=2, ensure_ascii=False)}

Retourne un JSON avec cette structure EXACTE :
{{
  "match": {{
    "global_score": 0,
    "technical_score": 0,
    "experience_score": 0,
    "missing_skills": [],
    "strengths": [],
    "summary": ""
  }}
}}
"""

    result = ask_ai_json(system_prompt, user_prompt)

    if "match" in result:
        return result["match"]
    return result


# ==============================================================
# 🔹 GÉNÉRATION LETTRE DE MOTIVATION (AJOUTÉE)
# ==============================================================

def generate_cover_letter(
    cv_analysis: Dict[str, Any],
    offer: Dict[str, Any],
    match_result: Dict[str, Any]
) -> str:
    """
    🎯 Génère une lettre de motivation personnalisée

    📚 EXPLICATION :
    Cette fonction prend l'analyse du CV, l'offre et les résultats du matching
    pour générer une lettre de motivation sur mesure.

    Args:
        cv_analysis: Analyse du CV (skills, expérience...)
        offer: L'offre d'emploi (titre, entreprise, description)
        match_result: Résultats du matching (points forts, etc.)

    Returns:
        str: La lettre de motivation générée
    """

    # Extraire les informations pertinentes
    cv_summary = cv_analysis.get("analysis", {}).get("resume", "")
    cv_skills = cv_analysis.get("analysis", {}).get("hard_skills", [])

    job_title = offer.get("title", "")
    company = offer.get("company", "")
    job_description = offer.get("description", "")[:500]

    strengths = match_result.get("strengths", [])
    match_score = match_result.get("global_score", 0)

    system_prompt = """Tu es un expert en rédaction de lettres de motivation.
    Rédige une lettre professionnelle, personnalisée et convaincante.
    Sois concis (max 200 mots) et va à l'essentiel.
    Utilise un ton enthousiaste mais professionnel."""

    user_prompt = f"""
Rédige une lettre de motivation pour postuler au poste suivant :

--- OFFRE ---
Titre : {job_title}
Entreprise : {company}
Description : {job_description}

--- PROFIL CANDIDAT ---
Résumé : {cv_summary}
Compétences principales : {', '.join(cv_skills[:5])}

--- MATCHING ---
Score de compatibilité : {match_score}%
Points forts identifiés : {', '.join(strengths) if strengths else 'Profil correspondant aux exigences'}

Instructions :
- Adresse-toi au recruteur
- Explique pourquoi tu es intéressé par ce poste
- Mets en avant tes compétences qui correspondent à l'offre
- Termine par une formule de politesse professionnelle

Retourne UNIQUEMENT le texte de la lettre, sans aucun commentaire.
"""

    return ask_ai(system_prompt, user_prompt, temperature=0.7)


# ==============================================================
# 🔹 OPTIMISATION CV (AJOUTÉE)
# ==============================================================

def optimize_cv_for_offer(
    cv_analysis: Dict[str, Any],
    offer_analysis: Dict[str, Any],
    match_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    🎯 Génère un CV optimisé pour une offre spécifique

    Args:
        cv_analysis: Analyse du CV original
        offer_analysis: Analyse de l'offre
        match_result: Résultats du matching

    Returns:
        Dict: CV optimisé (summary, skills, achievements)
    """

    system_prompt = """Tu es expert en optimisation CV pour ATS.
    Réponds uniquement au format JSON.
    Ne mens pas sur les compétences, mais mets en valeur celles qui correspondent."""

    user_prompt = f"""
Optimise ce CV pour l'offre ciblée.

CV ORIGINAL :
{json.dumps(cv_analysis, indent=2, ensure_ascii=False)}

OFFRE CIBLÉE :
{json.dumps(offer_analysis, indent=2, ensure_ascii=False)}

RÉSULTAT DU MATCHING :
{json.dumps(match_result, indent=2, ensure_ascii=False)}

Retourne un JSON avec cette structure :
{{
  "optimized_cv": {{
    "summary": "résumé professionnel optimisé (2-3 phrases)",
    "skills": ["compétence1", "compétence2"],
    "achievements": ["accomplissement1", "accomplissement2"]
  }}
}}
"""

    result = ask_ai_json(system_prompt, user_prompt, temperature=0.3)

    if "optimized_cv" in result:
        return result["optimized_cv"]
    return result


# ==============================================================
# 🔹 SCORING AVANCÉ (AJOUTÉ)
# ==============================================================

def score_analysis(
    cv_analysis: Dict[str, Any],
    offer_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    🎯 Calcule un score détaillé entre CV et offre

    Returns:
        Dict: Scores détaillés (global, technique, expérience)
    """

    system_prompt = "Tu es expert scoring RH. Réponds uniquement au format JSON."

    user_prompt = f"""
Compare et donne un score détaillé :

CV :
{json.dumps(cv_analysis, indent=2, ensure_ascii=False)}

OFFRE :
{json.dumps(offer_analysis, indent=2, ensure_ascii=False)}

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

    result = ask_ai_json(system_prompt, user_prompt)

    if "score" in result:
        return result["score"]
    return result


# ==============================================================
# 🔹 PIPELINE COMPLET (AJOUTÉ)
# ==============================================================

def auto_apply_pipeline(
    cv_text: str,
    offer: Dict[str, Any],
    cv_analysis: Optional[Dict[str, Any]] = None,
    offer_analysis: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    🔥 Pipeline complet : analyse, matching, génération

    Returns:
        Dict: Tous les résultats du pipeline
    """

    logger.info("Démarrage du pipeline auto-apply")

    # Étape 1: Analyse CV
    if cv_analysis is None:
        logger.info("Analyse du CV...")
        cv_analysis = analyze_cv(cv_text)

    # Étape 2: Analyse offre
    if offer_analysis is None:
        logger.info("Analyse de l'offre...")
        offer_analysis = analyze_offer(offer)

    # Étape 3: Matching
    logger.info("Calcul du matching...")
    match_result = match_cv_offer(cv_analysis, offer_analysis)

    # Étape 4: Optimisation CV
    logger.info("Optimisation du CV...")
    optimized_cv = optimize_cv_for_offer(cv_analysis, offer_analysis, match_result)

    # Étape 5: Génération lettre
    logger.info("Génération de la lettre...")
    cover_letter = generate_cover_letter(cv_analysis, offer, match_result)

    logger.info("Pipeline terminé")

    return {
        "cv_analysis": cv_analysis,
        "offer_analysis": offer_analysis,
        "match": match_result,
        "optimized_cv": optimized_cv,
        "cover_letter": cover_letter
    }
    
# ==============================================================
# 🔹 AUTO APPLY (FULL PIPELINE IA) - ALIAS
# ==============================================================

def auto_apply(
    cv_text: str,
    offer: Dict[str, Any],
    cv_analysis: Optional[Dict[str, Any]] = None,
    offer_analysis: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    🔥 MODE FULL AUTOMATIQUE (ALIAS)

    📚 POUR UN DÉBUTANT :
    Cette fonction est un alias de auto_apply_pipeline pour assurer
    la compatibilité avec le code existant.

    Elle génère directement :
    - lettre de motivation
    - CV optimisé
    - analyse complète

    Args:
        cv_text: Texte brut du CV
        offer: Offre d'emploi (dictionnaire)
        cv_analysis: Analyse CV pré-calculée (optionnel)
        offer_analysis: Analyse offre pré-calculée (optionnel)

    Returns:
        Dict: Résultats complets du pipeline
    """

    logger.info("🚀 Lancement de auto_apply (mode full automatique)")

    # Appel du pipeline complet
    result = auto_apply_pipeline(
        cv_text=cv_text,
        offer=offer,
        cv_analysis=cv_analysis,
        offer_analysis=offer_analysis
    )

    # Format de sortie compatible avec l'ancienne version
    return {
        "auto_apply": {
            "cover_letter": result.get("cover_letter", ""),
            "optimized_cv": result.get("optimized_cv", {}),
            "match_score": result.get("match", {}).get("global_score", 0)
        }
    }