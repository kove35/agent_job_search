"""
=====================================================================
📦 APPLICATION STORAGE (GESTION DES CANDIDATURES EN BASE DE DONNÉES)
=====================================================================

🎯 RÔLE :
Ce fichier s'occupe de TOUT ce qui concerne les candidatures en base de données :
- sauvegarder une candidature (CREATE)
- lister les candidatures (READ)
- trouver une candidature par son ID (READ BY ID)
- trouver les candidatures pour une offre (READ BY JOB ID)
- mettre à jour le statut d'une candidature (UPDATE)
- supprimer une candidature (DELETE)
- obtenir des statistiques (STATS)

📚 POUR UN DÉBUTANT :
Imagine un grand cahier (la base de données) où on note chaque candidature.
Ce fichier est le secrétaire qui sait :
- écrire une nouvelle ligne (sauvegarder)
- lire toutes les lignes (lister)
- retrouver une ligne précise (par ID)
- modifier une ligne (changer le statut)
- effacer une ligne (supprimer)
- faire des comptes (statistiques)

=====================================================================
"""

# ==============================================================
# 🔹 IMPORTS
# ==============================================================

from app.db.database import SessionLocal
from app.db.models import Application
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging

# Configuration du logging pour voir ce qui se passe
logger = logging.getLogger(__name__)


# ==============================================================
# 💾 CREATE - SAUVEGARDER UNE CANDIDATURE
# ==============================================================

def save_application(data: Dict[str, Any]) -> Optional[int]:
    """
    🎯 Sauvegarde une candidature en base de données

    📚 EXPLICATION :
    Cette fonction prend un dictionnaire avec les infos de la candidature
    et l'ajoute dans la table "applications" de la base de données.

    Args:
        data: Dictionnaire contenant :
            - job_id (str): ID de l'offre (OBLIGATOIRE)
            - title (str): Titre du poste
            - company (str): Nom de l'entreprise
            - status (str): Statut ("pending", "sent", "accepted", "rejected")
            - score (int): Score de matching (0-100)
            - cover_letter (str): Lettre de motivation
            - optimized_cv (str): Chemin du CV optimisé

    Returns:
        int: L'ID de la candidature créée, ou None si erreur
    """

    # Ouverture de la session DB
    db = SessionLocal()

    try:
        # Création de l'objet Application
        application = Application(
            job_id=data.get("job_id", ""),
            title=data.get("title", ""),
            company=data.get("company", ""),
            status=data.get("status", "pending"),
            score=data.get("score", 0),
            cover_letter=data.get("cover_letter"),
            optimized_cv_path=data.get("optimized_cv"),
            created_at=datetime.now(timezone.utc)
        )

        # Ajout à la session
        db.add(application)

        # Validation (sauvegarde effective)
        db.commit()

        # Rafraîchissement pour récupérer l'ID généré
        db.refresh(application)

        # Log de succès
        logger.info(f"✅ Candidature sauvegardée - ID: {application.id}")

        return application.id

    except Exception as e:
        # En cas d'erreur, on annule (rollback)
        db.rollback()
        logger.error(f"❌ Erreur DB: {e}")
        return None

    finally:
        # Toujours fermer la session
        db.close()


# ==============================================================
# 📖 READ ALL - RÉCUPÉRER TOUTES LES CANDIDATURES
# ==============================================================

def get_applications(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    🎯 Récupère toutes les candidatures (avec pagination)

    Args:
        limit: Nombre maximum de résultats
        offset: Décalage pour la pagination

    Returns:
        List[Dict]: Liste des candidatures
    """

    db = SessionLocal()

    try:
        apps = db.query(Application)\
            .order_by(Application.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()

        result = []
        for app in apps:
            result.append({
                "id": app.id,
                "job_id": app.job_id,
                "title": app.title,
                "company": app.company,
                "status": app.status,
                "score": app.score,
                "cover_letter": app.cover_letter,
                "created_at": app.created_at.isoformat() if app.created_at else None
            })

        logger.info(f"📋 {len(result)} candidatures récupérées")
        return result

    except Exception as e:
        logger.error(f"❌ Erreur DB: {e}")
        return []

    finally:
        db.close()


# ==============================================================
# 🔍 READ BY ID - RÉCUPÉRER UNE CANDIDATURE PAR SON ID
# ==============================================================

def get_application_by_id(application_id: int) -> Optional[Dict[str, Any]]:
    """
    🎯 Récupère une candidature spécifique par son ID

    Args:
        application_id: L'ID de la candidature

    Returns:
        Dict: La candidature, ou None si non trouvée
    """

    db = SessionLocal()

    try:
        app = db.query(Application).filter(Application.id == application_id).first()

        if not app:
            logger.warning(f"Candidature {application_id} non trouvée")
            return None

        return {
            "id": app.id,
            "job_id": app.job_id,
            "title": app.title,
            "company": app.company,
            "status": app.status,
            "score": app.score,
            "cover_letter": app.cover_letter,
            "optimized_cv": app.optimized_cv_path,
            "created_at": app.created_at.isoformat() if app.created_at else None,
            "updated_at": app.updated_at.isoformat() if hasattr(app, 'updated_at') and app.updated_at else None
        }

    except Exception as e:
        logger.error(f"❌ Erreur DB: {e}")
        return None

    finally:
        db.close()


# ==============================================================
# 🔍 READ BY JOB ID - CANDIDATURES POUR UNE OFFRE
# ==============================================================

def get_applications_by_job_id(job_id: str) -> List[Dict[str, Any]]:
    """
    🎯 Récupère toutes les candidatures pour une offre spécifique

    Args:
        job_id: L'ID de l'offre

    Returns:
        List[Dict]: Liste des candidatures pour cette offre
    """

    db = SessionLocal()

    try:
        apps = db.query(Application).filter(Application.job_id == job_id).all()

        result = []
        for app in apps:
            result.append({
                "id": app.id,
                "status": app.status,
                "score": app.score,
                "created_at": app.created_at.isoformat() if app.created_at else None
            })

        logger.info(f"📋 {len(result)} candidatures pour l'offre {job_id}")
        return result

    except Exception as e:
        logger.error(f"❌ Erreur DB: {e}")
        return []

    finally:
        db.close()


# ==============================================================
# 🔄 UPDATE - METTRE À JOUR LE STATUT D'UNE CANDIDATURE
# ==============================================================

def update_application_status(application_id: int, status: str) -> bool:
    """
    🎯 Met à jour le statut d'une candidature

    Statuts possibles:
        - pending: en attente
        - sent: envoyée
        - accepted: acceptée
        - rejected: refusée

    Args:
        application_id: ID de la candidature
        status: Nouveau statut

    Returns:
        bool: True si mise à jour réussie, False sinon
    """

    db = SessionLocal()

    try:
        app = db.query(Application).filter(Application.id == application_id).first()

        if not app:
            logger.warning(f"Candidature {application_id} non trouvée")
            return False

        app.status = status
        app.updated_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"✅ Candidature {application_id} → statut: {status}")
        return True

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur DB: {e}")
        return False

    finally:
        db.close()


# ==============================================================
# ❌ DELETE - SUPPRIMER UNE CANDIDATURE
# ==============================================================

def delete_application(application_id: int) -> bool:
    """
    🎯 Supprime une candidature

    ⚠️ ATTENTION : Cette action est irréversible !

    Args:
        application_id: ID de la candidature à supprimer

    Returns:
        bool: True si suppression réussie, False sinon
    """

    db = SessionLocal()

    try:
        app = db.query(Application).filter(Application.id == application_id).first()

        if not app:
            logger.warning(f"Candidature {application_id} non trouvée")
            return False

        db.delete(app)
        db.commit()

        logger.info(f"✅ Candidature {application_id} supprimée")
        return True

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur DB: {e}")
        return False

    finally:
        db.close()


# ==============================================================
# 📊 STATISTIQUES - OBTENIR DES STATS SUR LES CANDIDATURES
# ==============================================================

def get_applications_stats() -> Dict[str, Any]:
    """
    🎯 Récupère des statistiques sur les candidatures

    Returns:
        Dict: Un dictionnaire avec les statistiques
    """

    db = SessionLocal()

    try:
        apps = db.query(Application).all()

        stats = {
            "total": len(apps),
            "by_status": {
                "pending": 0,
                "sent": 0,
                "accepted": 0,
                "rejected": 0
            },
            "average_score": 0,
            "total_score": 0
        }

        for app in apps:
            status = app.status or "pending"
            if status in stats["by_status"]:
                stats["by_status"][status] += 1

            if app.score:
                stats["total_score"] += app.score

        if stats["total"] > 0:
            stats["average_score"] = round(stats["total_score"] / stats["total"], 2)

        logger.info(f"📊 Stats: {stats['total']} candidatures, score moyen: {stats['average_score']}")
        return stats

    except Exception as e:
        logger.error(f"❌ Erreur DB: {e}")
        return {"total": 0, "by_status": {}, "average_score": 0, "total_score": 0}

    finally:
        db.close()
        
# ==============================================================
# 🔹 ALIAS POUR RÉTROCOMPATIBILITÉ (PLACÉ ICI, APRÈS LA DÉFINITION)
# ==============================================================

# ✅ IMPORTANT : L'alias doit être APRÈS la définition de la fonction
save_application_pack = save_application