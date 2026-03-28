"""
=====================================================================
🔍 JOB SEARCH SERVICE - GESTION DES OFFRES D'EMPLOI
=====================================================================

🎯 RÔLE :
Ce fichier s'occupe de :
- récupérer des offres depuis l'API Adzuna
- normaliser les données
- analyser les offres avec l'IA
- sauvegarder en base de données
- enrichir les offres pour l'agent

📚 POUR UN DÉBUTANT :
C'est le "chef d'orchestre" pour tout ce qui concerne les offres d'emploi.

=====================================================================
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.services.ai_agent import analyze_offer
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import Job

# Configuration du logging
logger = logging.getLogger(__name__)


# ==============================================================
# 🔹 CLASSE ADAPTATEUR (pour l'analyse IA)
# ==============================================================

class OfferObj:
    """
    📚 POUR UN DÉBUTANT :
    Cette classe transforme un dictionnaire d'offre en objet
    que l'IA peut comprendre.
    """

    def __init__(self, data: Dict[str, Any]):
        self.title = data.get("title")
        self.description = data.get("description")
        self.location = data.get("location")
        self.company = data.get("company")


# ==============================================================
# 🔹 RÉCUPÉRATION DES OFFRES (API Adzuna)
# ==============================================================

def fetch_job_offers(
    max_pages: int = 1,
    results_per_page: int = 5,
    what: str = "",
    where: str = ""
) -> List[Dict[str, Any]]:
    """
    🎯 Récupère des offres d'emploi depuis l'API Adzuna

    Args:
        max_pages: Nombre de pages à récupérer
        results_per_page: Nombre de résultats par page
        what: Mots-clés de recherche
        where: Localisation

    Returns:
        List[Dict]: Liste brute des offres
    """

    base_url = "https://api.adzuna.com/v1/api/jobs/fr/search/"
    all_offers = []

    # Utiliser les valeurs par défaut de la config si non spécifiées
    if not what:
        what = getattr(settings, "JOB_KEYWORD", "")
    if not where:
        where = getattr(settings, "JOB_LOCATION", "")

    logger.info(f"🔍 Récupération des offres: what='{what}', where='{where}'")

    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}"

        params = {
            "app_id": settings.ADZUNA_APP_ID,
            "app_key": settings.ADZUNA_APP_KEY,
            "results_per_page": results_per_page,
            "what": what,
            "where": where
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            offers = data.get("results", [])
            all_offers.extend(offers)

            logger.info(f"Page {page}: {len(offers)} offres récupérées")

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur API Adzuna page {page}: {e}")
            continue

    logger.info(f"✅ Total: {len(all_offers)} offres récupérées")
    return all_offers


# ==============================================================
# 🔹 NORMALISATION D'UNE OFFRE
# ==============================================================

def normalize_offer(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    🎯 Normalise une offre brute en format standard

    Args:
        item: Offre brute de l'API

    Returns:
        Dict: Offre normalisée
    """

    return {
        "title": item.get("title", ""),
        "company": item.get("company", {}).get("display_name", ""),
        "location": item.get("location", {}).get("display_name", ""),
        "description": item.get("description", ""),
        "url": item.get("redirect_url", ""),
        "id": item.get("id", ""),
        "created_at": item.get("created", "")
    }


# ==============================================================
# 🔹 ENRICHISSEMENT D'UNE OFFRE (pour l'agent)
# ==============================================================

def enrich_job_offer(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    🎯 Enrichit une offre d'emploi avec des données supplémentaires

    📚 EXPLICATION :
    Cette fonction prend une offre brute et ajoute :
    - une date de récupération
    - un score par défaut
    - un statut

    Args:
        job: Dictionnaire de l'offre

    Returns:
        Dict: Offre enrichie
    """

    if not job:
        return {}

    # Création d'une copie pour ne pas modifier l'original
    enriched = job.copy()

    # Ajout de la date de récupération
    if "retrieved_at" not in enriched:
        enriched["retrieved_at"] = datetime.now().isoformat()

    # Ajout d'un score par défaut
    if "match_score" not in enriched:
        enriched["match_score"] = 0

    # Ajout d'un statut par défaut
    if "status" not in enriched:
        enriched["status"] = "pending"

    # S'assurer que les champs essentiels existent
    enriched.setdefault("title", "")
    enriched.setdefault("company", "")
    enriched.setdefault("location", "")
    enriched.setdefault("description", "")
    enriched.setdefault("url", "")
    enriched.setdefault("id", "")

    logger.debug(f"Offre enrichie: {enriched.get('title', 'Sans titre')}")
    return enriched


# ==============================================================
# 🔹 PIPELINE COMPLET (fetch + analyse + store)
# ==============================================================

def fetch_and_store_job_offers(
    max_pages: int = 1,
    results_per_page: int = 5,
    what: str = "",
    where: str = "",
    save_to_db: bool = True
) -> List[Dict[str, Any]]:
    """
    🎯 Pipeline complet :
    1. Récupère les offres
    2. Normalise
    3. Analyse avec IA
    4. Sauvegarde en DB

    Returns:
        List[Dict]: Liste des offres analysées
    """

    logger.info("🚀 PIPELINE START")

    # 1️⃣ Récupération des offres
    raw_offers = fetch_job_offers(max_pages, results_per_page, what, where)

    if not raw_offers:
        logger.warning("Aucune offre récupérée")
        return []

    analyzed_jobs = []

    # 2️⃣ Analyse de chaque offre
    for item in raw_offers:
        try:
            # Normalisation
            offer = normalize_offer(item)

            logger.info(f"🔍 Analyse : {offer.get('title')} - {offer.get('company')}")

            # Analyse IA
            analysis = analyze_offer(OfferObj(offer))

            analyzed_jobs.append({
                "offer": offer,
                "analysis": analysis,
                "raw": item
            })

        except Exception as e:
            logger.error(f"❌ Erreur analyse: {e}")
            continue

    # 3️⃣ Sauvegarde en base de données
    if save_to_db:
        db = SessionLocal()
        saved_count = 0

        try:
            for job_data in analyzed_jobs:
                offer = job_data["offer"]

                # Vérifier si l'offre existe déjà
                exists = db.query(Job).filter(
                    Job.title == offer.get("title"),
                    Job.company == offer.get("company")
                ).first()

                if exists:
                    logger.debug(f"Offre déjà existante: {offer.get('title')}")
                    continue

                # Création de l'objet Job
                job = Job(
                    title=offer.get("title"),
                    company=offer.get("company"),
                    location=offer.get("location"),
                    description=offer.get("description"),
                    external_id=offer.get("id"),
                    url=offer.get("url")
                )

                db.add(job)
                saved_count += 1

            db.commit()
            logger.info(f"✅ {saved_count} jobs sauvegardés en DB")

        except Exception as e:
            db.rollback()
            logger.error(f"❌ Erreur sauvegarde DB: {e}")
        finally:
            db.close()

    logger.info(f"🏁 Pipeline terminé: {len(analyzed_jobs)} offres analysées")
    return analyzed_jobs


# ==============================================================
# 🔹 RECHERCHE PAR COMPÉTENCES
# ==============================================================

def search_jobs_by_skills(
    skills: List[str],
    max_pages: int = 1,
    results_per_page: int = 10,
    location: str = ""
) -> List[Dict[str, Any]]:
    """
    🎯 Recherche des offres basées sur des compétences

    Args:
        skills: Liste des compétences (ex: ["Python", "Data Science"])
        max_pages: Nombre de pages
        results_per_page: Résultats par page
        location: Localisation

    Returns:
        List[Dict]: Liste des offres enrichies
    """

    what = " ".join(skills)
    logger.info(f"🔍 Recherche par compétences: {what}")

    raw_offers = fetch_job_offers(
        max_pages=max_pages,
        results_per_page=results_per_page,
        what=what,
        where=location
    )

    # Enrichissement des offres
    enriched_offers = []
    for offer in raw_offers:
        normalized = normalize_offer(offer)
        enriched = enrich_job_offer(normalized)
        enriched_offers.append(enriched)

    return enriched_offers


# ==============================================================
# 🔹 RECHERCHE PAR TITRE
# ==============================================================

def search_jobs_by_title(
    title: str,
    max_pages: int = 1,
    results_per_page: int = 10,
    location: str = ""
) -> List[Dict[str, Any]]:
    """
    🎯 Recherche des offres par titre

    Args:
        title: Titre du poste
        max_pages: Nombre de pages
        results_per_page: Résultats par page
        location: Localisation

    Returns:
        List[Dict]: Liste des offres enrichies
    """

    logger.info(f"🔍 Recherche par titre: {title}")

    raw_offers = fetch_job_offers(
        max_pages=max_pages,
        results_per_page=results_per_page,
        what=title,
        where=location
    )

    # Enrichissement des offres
    enriched_offers = []
    for offer in raw_offers:
        normalized = normalize_offer(offer)
        enriched = enrich_job_offer(normalized)
        enriched_offers.append(enriched)

    return enriched_offers


# ==============================================================
# 🔹 FONCTION DE TEST
# ==============================================================

def test_job_search() -> bool:
    """
    🎯 Teste la recherche d'offres

    Returns:
        bool: True si le test réussit
    """

    logger.info("🔧 Test de recherche d'offres...")

    try:
        offers = fetch_job_offers(max_pages=1, results_per_page=3)

        if offers:
            logger.info(f"✅ Test réussi: {len(offers)} offres trouvées")
            logger.info(f"   Exemple: {offers[0].get('title', 'Sans titre')}")
            return True
        else:
            logger.error("❌ Aucune offre trouvée")
            return False

    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
        return False