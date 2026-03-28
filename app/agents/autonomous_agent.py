"""
=====================================================================
🤖 AGENT AUTONOME - VERSION CORRIGÉE AVEC BASE DE DONNÉES
=====================================================================

🎯 RÔLE :
C'est le cœur de l'automatisation. Cet agent :
1. Récupère des offres d'emploi via l'API Adzuna
2. Analyse chaque offre avec l'IA
3. Compare avec le CV analysé
4. Décide s'il faut postuler (score > seuil)
5. Génère les candidatures et les sauvegarde en DB

📚 POUR UN DÉBUTANT :
Imagine un assistant qui cherche du travail à ta place.
Il lit les offres, voit si ça correspond à ton CV,
et prépare des candidatures pour celles qui sont intéressantes.

=====================================================================
"""

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

# ==============================================================
# 🔹 IMPORTS SERVICES
# ==============================================================
from app.services.adzuna_api import fetch_jobs_from_adzuna
from app.services.job_search import enrich_job_offer
from app.services.cv_extraction import extract_text_from_pdf
from app.services.ai_agent import (
    analyze_cv,
    analyze_offer,
    match_cv_offer,
    generate_cover_letter,
    optimize_cv_for_offer
)
from app.services.scoring import compute_smart_score

# ✅ CORRIGÉ : Utilisation des bons imports pour la DB
from app.services.storage.application_storage import save_application
from app.services.storage.cv_storage import get_cv_path, save_cv

# ==============================================================
# 🔹 LOGGING
# ==============================================================
logger = logging.getLogger(__name__)


# ==============================================================
# 🔹 DATACLASSES
# ==============================================================

@dataclass
class ProcessedJob:
    """
    📚 POUR UN DÉBUTANT :
    Une dataclass est comme un "moule" pour stocker toutes les infos
    d'une offre traitée. C'est plus propre qu'un dictionnaire.
    """
    job_id: str
    title: str
    company: str
    location: str
    description: str
    url: str
    analysis: Dict[str, Any] = field(default_factory=dict)
    match_score: int = 0
    missing_skills: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    should_apply: bool = False
    cover_letter: Optional[str] = None
    optimized_cv: Optional[Dict] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentResult:
    """Résultat final de l'agent"""
    success: bool = False
    jobs_processed: int = 0
    applications_generated: int = 0
    jobs: List[ProcessedJob] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# ==============================================================
# 🔹 FONCTION DE DÉCISION
# ==============================================================

def should_apply_to_job(match_score: int, missing_skills: List[str]) -> bool:
    """
    🎯 Décide si on doit postuler à une offre

    📚 POUR UN DÉBUTANT :
    Cette fonction prend le score de matching et les compétences manquantes
    et décide si l'offre vaut le coup.

    Règles :
    - Score >= 70% → postuler (excellent match)
    - Score entre 50% et 70% → postuler si peu de compétences manquantes (≤ 3)
    - Score < 50% → ne pas postuler

    Ces règles peuvent être modifiées selon tes besoins.
    """

    if match_score >= 70:
        logger.debug(f"Score élevé ({match_score}%) → candidature")
        return True

    if match_score >= 50 and len(missing_skills) <= 3:
        logger.debug(f"Score moyen ({match_score}%) mais seulement {len(missing_skills)} compétences manquantes → candidature")
        return True

    logger.debug(f"Score trop bas ({match_score}%) → pas de candidature")
    return False


# ==============================================================
# 🔹 ANALYSE D'UNE OFFRE INDIVIDUELLE
# ==============================================================

def analyze_single_job(
    job: Dict[str, Any],
    cv_analysis: Dict[str, Any],
    threshold: int = 20
) -> ProcessedJob:
    """
    🔍 Analyse une offre et décide si on postule

    📚 POUR UN DÉBUTANT :
    Cette fonction fait tout le travail pour UNE offre :
    - Analyse l'offre avec l'IA
    - Calcule le score de matching avec le CV
    - Décide si on postule
    - Génère les documents si besoin
    """

    logger.info(f"Analyse de l'offre: {job.get('title', 'Sans titre')} - {job.get('company', '')}")

    # ==========================================================
    # 1️⃣ ANALYSE DE L'OFFRE AVEC L'IA
    # ==========================================================
    try:
        offer_analysis = analyze_offer(job)
        logger.debug("Analyse de l'offre terminée")
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de l'offre: {e}")
        offer_analysis = {"analysis": {"hard_skills": [], "soft_skills": []}}

    # ==========================================================
    # 2️⃣ MATCHING CV / OFFRE
    # ==========================================================
    try:
        match_result = match_cv_offer(cv_analysis, offer_analysis)
        
        match_score = match_result.get("global_score", 0)
        missing_skills = match_result.get("missing_skills", [])
        strengths = match_result.get("strengths", [])
        
        # Fallback : si score = 0, utiliser compute_smart_score
        if match_score == 0:
            profile = {
                "skills": cv_analysis.get("analysis", {}).get("hard_skills", []),
                "job_targets": []
            }
            match_score, _ = compute_smart_score(job, profile)
        
        logger.info(f"Score de matching: {match_score}% - Manquants: {len(missing_skills)}")
    except Exception as e:
        logger.error(f"Erreur lors du matching: {e}")
        match_score = 0
        missing_skills = []
        strengths = []

    # ==========================================================
    # 3️⃣ DÉCISION DE POSTULER
    # ==========================================================
    should_apply = should_apply_to_job(match_score, missing_skills)

    # ==========================================================
    # 4️⃣ CRÉATION DE L'OBJET RÉSULTAT
    # ==========================================================
    processed_job = ProcessedJob(
        job_id=job.get("id", job.get("job_id", "")),
        title=job.get("title", ""),
        company=job.get("company", ""),
        location=job.get("location", ""),
        description=job.get("description", ""),
        url=job.get("url", job.get("redirect_url", "")),
        analysis=offer_analysis,
        match_score=match_score,
        missing_skills=missing_skills,
        strengths=strengths,
        should_apply=should_apply
    )

    # ==========================================================
    # 5️⃣ SI ON POSTULE : GÉNÉRATION DES DOCUMENTS
    # ==========================================================
    if should_apply and match_score >= threshold:
        logger.info(f"📝 Génération des documents pour {processed_job.title}")
        
        try:
            # Lettre de motivation
            cover_letter = generate_cover_letter(
                cv_analysis=cv_analysis,
                offer=job,
                match_result=match_result
            )
            processed_job.cover_letter = cover_letter
            
            # CV optimisé
            optimized_cv = optimize_cv_for_offer(
                cv_analysis=cv_analysis,
                offer_analysis=offer_analysis,
                match_result=match_result
            )
            processed_job.optimized_cv = optimized_cv
            
            logger.debug(f"✅ Documents générés pour {processed_job.title}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des documents: {e}")
            processed_job.cover_letter = f"Erreur de génération: {str(e)}"

    return processed_job


# ==============================================================
# 🔹 AGENT PRINCIPAL
# ==============================================================

def run_autonomous_agent(
    cv_pdf_path: str,
    user_id: Optional[int] = None,
    max_jobs: int = 10,
    location: str = "",
    threshold: int = 20,
    save_to_db: bool = True
) -> List[Dict[str, Any]]:
    """
    🤖 AGENT AUTONOME PRINCIPAL - VERSION CORRIGÉE

    🎯 Point d'entrée principal. Cette fonction :
    1. Extrait et analyse le CV
    2. Récupère des offres d'emploi
    3. Analyse chaque offre
    4. Décide si postuler
    5. Génère les documents
    6. Sauvegarde les candidatures en DB

    📚 POUR UN DÉBUTANT :
    C'est le "cerveau" principal. Tu appelles cette fonction
    avec le chemin de ton CV, et elle fait tout le reste.

    Args:
        cv_pdf_path: Chemin vers le fichier PDF du CV
        user_id: ID de l'utilisateur (pour la DB)
        max_jobs: Nombre maximum d'offres à récupérer
        location: Localisation (ex: "Paris", "Lyon")
        threshold: Score minimum pour postuler (0-100)
        save_to_db: Sauvegarder les candidatures en DB

    Returns:
        Liste des offres traitées (format compatible avec l'API)
    """

    logger.info("=" * 60)
    logger.info("🤖 DÉMARRAGE DE L'AGENT AUTONOME")
    logger.info(f"📄 CV: {cv_pdf_path}")
    logger.info(f"👤 User ID: {user_id}")
    logger.info(f"🎯 Max jobs: {max_jobs}, Location: {location or 'Toutes'}")
    logger.info(f"📊 Seuil de candidature: {threshold}%")
    logger.info("=" * 60)

    result = AgentResult()

    try:
        # ==========================================================
        # 📄 1️⃣ EXTRACTION ET ANALYSE DU CV
        # ==========================================================
        logger.info("📄 ÉTAPE 1: Extraction du CV...")
        
        if not os.path.exists(cv_pdf_path):
            raise FileNotFoundError(f"Le fichier CV n'existe pas: {cv_pdf_path}")

        cv_text = extract_text_from_pdf(cv_pdf_path)
        logger.info(f"CV extrait: {len(cv_text)} caractères")

        logger.info("🧠 Analyse du CV avec l'IA...")
        cv_analysis = analyze_cv(cv_text)
        logger.info("✅ Analyse du CV terminée")

        # ==========================================================
        # 🔍 2️⃣ RÉCUPÉRATION DES OFFRES
        # ==========================================================
        logger.info(f"🔍 ÉTAPE 2: Recherche d'offres (max: {max_jobs})...")
        
        try:
            jobs = fetch_jobs_from_adzuna(
                what="",  # Laisser vide, on utilise le CV pour les mots-clés
                where=location,
                max_results=max_jobs
            )
            logger.info(f"✅ Offres récupérées: {len(jobs)}")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des offres: {e}")
            jobs = []
            result.errors.append(f"Erreur Adzuna: {e}")

        # ==========================================================
        # 🔄 3️⃣ TRAITEMENT DE CHAQUE OFFRE
        # ==========================================================
        logger.info("🔄 ÉTAPE 3: Analyse des offres...")
        
        for idx, job in enumerate(jobs, 1):
            logger.info(f"--- Traitement {idx}/{len(jobs)} ---")
            
            try:
                # Enrichissement de l'offre
                job = enrich_job_offer(job)
                
                # Analyse de l'offre
                processed_job = analyze_single_job(
                    job=job,
                    cv_analysis=cv_analysis,
                    threshold=threshold
                )
                
                result.jobs.append(processed_job)
                result.jobs_processed += 1
                
                if processed_job.should_apply:
                    result.applications_generated += 1
                    logger.info(f"✅ CANDIDATURE GÉNÉRÉE: {processed_job.title} ({processed_job.match_score}%)")
                    
                    # Sauvegarde en DB
                    if save_to_db:
                        try:
                            app_id = save_application({
                                "job_id": processed_job.job_id,
                                "title": processed_job.title,
                                "company": processed_job.company,
                                "status": "draft",
                                "score": processed_job.match_score,
                                "cover_letter": processed_job.cover_letter
                            })
                            logger.debug(f"💾 Sauvegardé en DB - ID: {app_id}")
                        except Exception as e:
                            logger.warning(f"Erreur sauvegarde DB: {e}")
                else:
                    logger.debug(f"❌ NON RETENUE: {processed_job.title} ({processed_job.match_score}%)")
                    
            except Exception as e:
                logger.error(f"Erreur lors du traitement de l'offre: {e}")
                result.errors.append(f"Erreur sur offre {idx}: {e}")

        result.success = True
        
        logger.info("=" * 60)
        logger.info("📊 RÉSULTATS DE L'AGENT")
        logger.info(f"✅ Offres analysées: {result.jobs_processed}")
        logger.info(f"📝 Candidatures générées: {result.applications_generated}")
        logger.info(f"⚠️ Erreurs: {len(result.errors)}")
        logger.info("=" * 60)

        # ==========================================================
        # 4️⃣ FORMATAGE POUR L'API
        # ==========================================================
        output = []
        for job in result.jobs:
            output.append({
                "id": job.job_id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "url": job.url,
                "match_score": job.match_score,
                "missing_skills": job.missing_skills,
                "strengths": job.strengths,
                "cover_letter": job.cover_letter,
                "should_apply": job.should_apply
            })
        
        return output

    except Exception as e:
        logger.exception(f"❌ ERREUR FATALE DE L'AGENT: {e}")
        return [{"error": str(e)}]