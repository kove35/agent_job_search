"""
=====================================================================
🌐 ADZUNA API SERVICE - GESTION DES OFFRES D'EMPLOI
=====================================================================

🎯 RÔLE :
Ce fichier gère toutes les interactions avec l'API Adzuna pour :
- rechercher des offres d'emploi
- récupérer les détails d'une offre
- filtrer par localisation, mots-clés, etc.

📚 POUR UN DÉBUTANT :
Adzuna est un site d'offres d'emploi qui propose une API.
Ce fichier est le traducteur entre notre application et Adzuna.

=====================================================================
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configuration du logging
logger = logging.getLogger(__name__)

# ==============================================================
# 🔹 CONFIGURATION
# ==============================================================

from app.core.config import settings

# Paramètres API Adzuna
ADZUNA_APP_ID = settings.ADZUNA_APP_ID
ADZUNA_API_KEY = settings.ADZUNA_API_KEY  # ✅ Maintenant accessible via property
ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"

# Pays par défaut (fr = France)
DEFAULT_COUNTRY = "fr"


# ==============================================================
# 🔍 RECHERCHE D'OFFRES
# ==============================================================

def fetch_jobs_from_adzuna(
    what: str = "",
    where: str = "",
    max_results: int = 10,
    page: int = 1,
    country: str = DEFAULT_COUNTRY
) -> List[Dict[str, Any]]:
    """
    🎯 Récupère des offres d'emploi depuis l'API Adzuna

    📚 EXPLICATION :
    Cette fonction interroge l'API Adzuna avec les critères de recherche
    et retourne une liste d'offres d'emploi.

    Args:
        what: Mots-clés pour le poste (ex: "data scientist", "python")
        where: Localisation (ex: "Paris", "Lyon", "France")
        max_results: Nombre maximum d'offres à récupérer
        page: Numéro de page (pour la pagination)
        country: Code pays (fr, uk, us, etc.)

    Returns:
        List[Dict]: Liste des offres d'emploi
    """

    # Si aucun mot-clé n'est fourni, utiliser celui de la config
    if not what and settings.JOB_KEYWORD:
        what = settings.JOB_KEYWORD
        logger.info(f"Utilisation du mot-clé par défaut: {what}")

    # Si aucune localisation n'est fournie, utiliser celle de la config
    if not where and settings.JOB_LOCATION:
        where = settings.JOB_LOCATION
        logger.info(f"Utilisation de la localisation par défaut: {where}")

    logger.info(f"🔍 Recherche Adzuna: what='{what}', where='{where}', max={max_results}")

    # Construction de l'URL
    url = f"{ADZUNA_BASE_URL}/{country}/search/{page}"

    # Paramètres de la requête
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
        "results_per_page": max_results,
        "content-type": "application/json"
    }

    # Ajout des filtres si présents
    if what:
        params["what"] = what
    if where:
        params["where"] = where

    try:
        # Requête GET vers l'API
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        jobs = data.get("results", [])

        # Transformation des données
        formatted_jobs = []
        for job in jobs:
            formatted_jobs.append({
                "id": job.get("id", ""),
                "title": job.get("title", ""),
                "company": job.get("company", {}).get("display_name", ""),
                "description": job.get("description", ""),
                "location": job.get("location", {}).get("display_name", ""),
                "url": job.get("redirect_url", ""),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "created_at": job.get("created"),
                "category": job.get("category", {}).get("label", "")
            })

        logger.info(f"✅ {len(formatted_jobs)} offres récupérées")
        return formatted_jobs

    except requests.exceptions.Timeout:
        logger.error("❌ Timeout lors de l'appel API Adzuna")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur API Adzuna: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {e}")
        return []


# ==============================================================
# 🔍 RECHERCHE PAR MOTS-CLÉS (basée sur les compétences du CV)
# ==============================================================

def fetch_jobs_by_skills(
    skills: List[str],
    where: str = "",
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    🎯 Récupère des offres basées sur une liste de compétences

    Args:
        skills: Liste des compétences (ex: ["Python", "Machine Learning"])
        where: Localisation
        max_results: Nombre maximum d'offres

    Returns:
        List[Dict]: Liste des offres
    """

    # Concaténation des compétences
    what = " ".join(skills)

    logger.info(f"🔍 Recherche par compétences: {what}")

    return fetch_jobs_from_adzuna(
        what=what,
        where=where,
        max_results=max_results
    )


# ==============================================================
# 🔍 RECHERCHE PAR TITRE DE POSTE
# ==============================================================

def fetch_jobs_by_title(
    title: str,
    where: str = "",
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    🎯 Récupère des offres par titre de poste

    Args:
        title: Titre du poste (ex: "Data Scientist")
        where: Localisation
        max_results: Nombre maximum d'offres

    Returns:
        List[Dict]: Liste des offres
    """

    logger.info(f"🔍 Recherche par titre: {title}")

    return fetch_jobs_from_adzuna(
        what=title,
        where=where,
        max_results=max_results
    )


# ==============================================================
# 🔍 RECHERCHE D'UNE OFFRE PAR ID
# ==============================================================

def fetch_job_by_id(
    job_id: str,
    country: str = DEFAULT_COUNTRY
) -> Optional[Dict[str, Any]]:
    """
    🎯 Récupère une offre spécifique par son ID

    Args:
        job_id: L'ID de l'offre
        country: Code pays

    Returns:
        Dict: L'offre, ou None si non trouvée
    """

    logger.info(f"🔍 Recherche offre par ID: {job_id}")

    url = f"{ADZUNA_BASE_URL}/{country}/{job_id}"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
        "content-type": "application/json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        job = response.json()

        return {
            "id": job.get("id", ""),
            "title": job.get("title", ""),
            "company": job.get("company", {}).get("display_name", ""),
            "description": job.get("description", ""),
            "location": job.get("location", {}).get("display_name", ""),
            "url": job.get("redirect_url", ""),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "created_at": job.get("created"),
            "category": job.get("category", {}).get("label", "")
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur récupération offre {job_id}: {e}")
        return None


# ==============================================================
# 🔧 FONCTION DE TEST
# ==============================================================

def test_adzuna_connection() -> bool:
    """
    🎯 Teste la connexion à l'API Adzuna

    Returns:
        bool: True si la connexion fonctionne
    """

    logger.info("🔧 Test de connexion Adzuna...")

    jobs = fetch_jobs_from_adzuna(what="python", max_results=1)

    if jobs:
        logger.info("✅ Connexion Adzuna OK")
        return True
    else:
        logger.error("❌ Connexion Adzuna échouée")
        return False