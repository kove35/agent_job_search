"""
=====================================================================
💾 CV STORAGE SERVICE (GESTION DES FICHIERS CV) - VERSION COMPLÈTE
=====================================================================

🎯 RÔLE :
Ce fichier s'occupe de TOUT ce qui concerne les fichiers CV :
- sauvegarder un CV
- lister les CV existants
- supprimer un CV
- retrouver le chemin d'un CV
- obtenir des informations sur un CV (taille, date)
- gérer le dernier CV utilisé (pour le proposer par défaut)

📚 POUR UN DÉBUTANT :
Imagine une boîte à lettres (le dossier "storage/cv"). Ce fichier est
le facteur qui sait :
- où déposer une nouvelle lettre (sauvegarder)
- quelles lettres sont dans la boîte (lister)
- comment enlever une lettre (supprimer)
- où se trouve une lettre précise (chemin)
- quel poids et quelle date a une lettre (infos)
- quelle est la dernière lettre reçue (dernier CV)

=====================================================================
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configuration du logging
logger = logging.getLogger(__name__)

# ==============================================================
# 📂 CONFIGURATION - LES DOSSIERS OÙ SONT STOCKÉS LES FICHIERS
# ==============================================================

# CV_FOLDER : le dossier qui contient tous les CV
# Tous les fichiers PDF des CV seront stockés ici
CV_FOLDER = "storage/cv"

# LAST_CV_FILE : le fichier qui stocke le nom du dernier CV utilisé
# Il est stocké dans le dossier storage pour persister entre les sessions
LAST_CV_FILE = "storage/last_cv.json"

# Crée les dossiers s'ils n'existent pas
# exist_ok=True : ne pas générer d'erreur si le dossier existe déjà
os.makedirs(CV_FOLDER, exist_ok=True)
os.makedirs("storage", exist_ok=True)


# ==============================================================
# 💾 SAUVEGARDER LE DERNIER CV UTILISÉ
# ==============================================================

def save_last_cv(filename: str) -> bool:
    """
    🎯 Sauvegarde le nom du dernier CV utilisé

    📚 EXPLICATION :
    Cette fonction écrit dans un fichier JSON le nom du dernier CV
    qui a été utilisé. Ainsi, au prochain lancement, on peut le
    proposer par défaut.

    Args:
        filename: Le nom du CV à marquer comme dernier utilisé

    Returns:
        bool: True si la sauvegarde a réussi, False sinon
    """

    try:
        data = {
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        }
        with open(LAST_CV_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Dernier CV sauvegardé: {filename}")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde dernier CV: {e}")
        return False


def get_last_cv() -> Optional[str]:
    """
    🎯 Récupère le nom du dernier CV utilisé

    📚 EXPLICATION :
    Cette fonction lit le fichier JSON pour retrouver quel était le
    dernier CV utilisé lors de la session précédente.

    Returns:
        str: Le nom du dernier CV, ou None si aucun n'a été sauvegardé
    """

    try:
        if os.path.exists(LAST_CV_FILE):
            with open(LAST_CV_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                filename = data.get("filename")
                if filename:
                    logger.debug(f"📌 Dernier CV trouvé: {filename}")
                    return filename
        return None
    except Exception as e:
        logger.error(f"❌ Erreur lecture dernier CV: {e}")
        return None


def clear_last_cv() -> bool:
    """
    🎯 Efface la référence du dernier CV

    📚 EXPLICATION :
    Utile quand on supprime le dernier CV pour ne pas garder une
    référence obsolète.

    Returns:
        bool: True si l'effacement a réussi
    """

    try:
        if os.path.exists(LAST_CV_FILE):
            os.remove(LAST_CV_FILE)
            logger.info("🗑️ Référence du dernier CV effacée")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur effacement dernier CV: {e}")
        return False


def update_last_cv(filename: str) -> bool:
    """
    🎯 Met à jour le dernier CV utilisé (sans sauvegarder un nouveau fichier)

    📚 EXPLICATION :
    Utile quand on utilise un CV existant sans en uploader un nouveau.

    Args:
        filename: Le nom du CV à marquer comme dernier utilisé

    Returns:
        bool: True si la mise à jour a réussi
    """

    # Vérifier que le CV existe
    try:
        get_cv_path(filename)
        return save_last_cv(filename)
    except FileNotFoundError:
        logger.error(f"❌ Impossible de définir {filename} comme dernier CV: fichier introuvable")
        return False


def get_default_cv() -> Optional[str]:
    """
    🎯 Retourne le CV par défaut (le dernier utilisé, ou le plus récent)

    📚 EXPLICATION :
    Cette fonction est utilisée quand l'utilisateur ne spécifie pas de CV.
    Elle retourne :
    1. Le dernier CV utilisé (s'il existe)
    2. Sinon, le CV le plus récemment modifié
    3. Sinon, None

    Returns:
        str: Le nom du CV par défaut, ou None si aucun CV disponible
    """

    # 1️⃣ Essayer de récupérer le dernier CV utilisé
    last_cv = get_last_cv()
    if last_cv:
        try:
            # Vérifier qu'il existe toujours
            get_cv_path(last_cv)
            logger.info(f"📌 CV par défaut (dernier utilisé): {last_cv}")
            return last_cv
        except FileNotFoundError:
            logger.warning(f"⚠️ Le dernier CV {last_cv} n'existe plus, recherche d'un autre...")

    # 2️⃣ Sinon, prendre le CV le plus récent
    cvs = list_cvs()
    if cvs:
        logger.info(f"📌 CV par défaut (le plus récent): {cvs[0]}")
        return cvs[0]

    # 3️⃣ Aucun CV disponible
    logger.warning("⚠️ Aucun CV disponible")
    return None


# ==============================================================
# 💾 SAVE CV - SAUVEGARDER UN CV (VERSION AVEC TIMESTAMP)
# ==============================================================

def save_cv(filename: str, content: bytes, set_as_last: bool = True) -> str:
    """
    🎯 Sauvegarde un CV sur le disque

    📚 EXPLICATION :
    - filename : le nom du fichier (ex: "mon_cv.pdf")
    - content : le contenu binaire du fichier (les octets du PDF)
    - set_as_last : si True, définit ce CV comme dernier utilisé
    - retourne : le nom du fichier sauvegardé (avec timestamp)

    🔒 SÉCURITÉ :
    On utilise os.path.basename pour éviter les attaques de type
    "directory traversal" (ex: "../../../fichier_sensible")

    📅 TIMESTAMP :
    On ajoute un timestamp pour éviter les conflits de noms.
    Exemple: "mon_cv.pdf" → "mon_cv_20240324_143025.pdf"
    """

    # 🔒 Sécurité : on ne garde que le nom du fichier, pas le chemin
    safe_filename = os.path.basename(filename)

    # Ajouter un timestamp pour éviter les conflits de noms
    name, ext = os.path.splitext(safe_filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_filename = f"{name}_{timestamp}{ext}"

    # Construction du chemin complet
    path = os.path.join(CV_FOLDER, final_filename)

    # Écriture du fichier en mode binaire ("wb" = write binary)
    with open(path, "wb") as f:
        f.write(content)

    logger.info(f"💾 CV sauvegardé: {final_filename} ({len(content)} octets)")

    # Sauvegarde comme dernier CV utilisé si demandé
    if set_as_last:
        save_last_cv(final_filename)

    # On retourne le nom du fichier pour référence
    return final_filename


# ==============================================================
# 📂 LIST CVS - LISTER TOUS LES CV
# ==============================================================

def list_cvs() -> List[str]:
    """
    🎯 Retourne la liste de tous les CV disponibles

    📚 EXPLICATION :
    Cette fonction lit le dossier et retourne les noms de tous les fichiers
    qu'il contient.

    Returns:
        List[str]: Une liste des noms de fichiers
    """

    try:
        files = os.listdir(CV_FOLDER)
        # Filtrer pour ne garder que les fichiers PDF
        pdf_files = [f for f in files if f.endswith('.pdf')]
        # Trier par date de modification (du plus récent au plus ancien)
        pdf_files.sort(
            key=lambda f: os.path.getmtime(os.path.join(CV_FOLDER, f)),
            reverse=True
        )
        logger.debug(f"📂 {len(pdf_files)} CV trouvés")
        return pdf_files
    except Exception as e:
        logger.error(f"❌ Erreur lors du listage des CV: {e}")
        return []


# ==============================================================
# ❌ DELETE CV - SUPPRIMER UN CV
# ==============================================================

def delete_cv(filename: str) -> bool:
    """
    🎯 Supprime un CV du disque

    📚 EXPLICATION :
    - filename : le nom du fichier à supprimer
    - retourne : True si suppression réussie, False sinon

    🔒 SÉCURITÉ :
    On utilise basename pour éviter les attaques

    🧹 NETTOYAGE :
    Si le CV supprimé était le dernier utilisé, on efface la référence.
    """

    # 🔒 Sécurité : on nettoie le nom du fichier
    safe_filename = os.path.basename(filename)

    # Construction du chemin complet
    path = os.path.join(CV_FOLDER, safe_filename)

    # Vérification que le fichier existe
    if not os.path.exists(path):
        logger.warning(f"⚠️ Tentative de suppression d'un CV inexistant: {filename}")
        return False

    try:
        os.remove(path)
        logger.info(f"🗑️ CV supprimé: {safe_filename}")

        # Si c'était le dernier CV utilisé, effacer la référence
        last_cv = get_last_cv()
        if last_cv == safe_filename:
            clear_last_cv()
            logger.info(f"📌 Le CV supprimé était le dernier utilisé, référence effacée")

        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression de {filename}: {e}")
        return False


# ==============================================================
# 📄 GET CV PATH - OBTENIR LE CHEMIN COMPLET D'UN CV
# ==============================================================

def get_cv_path(filename: str) -> str:
    """
    🎯 Retourne le chemin complet d'un CV

    📚 EXPLICATION :
    - filename : le nom du fichier (ex: "mon_cv.pdf")
    - retourne : le chemin complet (ex: "storage/cv/mon_cv.pdf")

    ⚠️ Lève une exception si le fichier n'existe pas

    🔒 SÉCURITÉ :
    On utilise basename pour éviter les attaques
    """

    # 🔒 Sécurité : on nettoie le nom du fichier
    safe_filename = os.path.basename(filename)

    # Construction du chemin complet
    path = os.path.join(CV_FOLDER, safe_filename)

    # Vérification que le fichier existe
    if not os.path.exists(path):
        raise FileNotFoundError(f"CV introuvable : {filename}")

    return path


# ==============================================================
# ℹ️ GET CV INFO - OBTENIR LES INFORMATIONS D'UN CV
# ==============================================================

def get_cv_info(filename: str) -> Dict[str, Any]:
    """
    🎯 Récupère les informations d'un CV (taille, date de modification)

    📚 EXPLICATION :
    Cette fonction retourne des métadonnées sur le fichier CV :
    - son nom
    - sa taille en Ko (kilooctets)
    - sa date de dernière modification
    - s'il existe ou non
    - si c'est le dernier CV utilisé

    Returns:
        Dict: Un dictionnaire avec les informations
    """

    try:
        # On récupère d'abord le chemin
        path = get_cv_path(filename)

        # os.stat() retourne les informations du fichier
        stat = os.stat(path)

        # Récupérer le dernier CV pour comparaison
        last_cv = get_last_cv()
        is_last = (last_cv == filename)

        # Construction du dictionnaire de résultats
        return {
            "filename": filename,                      # Nom du fichier
            "exists": True,                            # Le fichier existe
            "size_kb": round(stat.st_size / 1024, 2),  # Taille en Ko (arrondie)
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),  # Date modif
            "is_last": is_last                         # True si c'est le dernier CV
        }

    except FileNotFoundError:
        # Si le fichier n'existe pas, on retourne une erreur
        return {
            "filename": filename,
            "exists": False,
            "error": "Fichier non trouvé"
        }

    except Exception as e:
        # Pour toute autre erreur
        return {
            "filename": filename,
            "exists": False,
            "error": str(e)
        }
        
# app/services/storage/cv_storage.py

# ... code existant ...

# ==============================================================
# 🔧 FONCTIONS D'EXTRACTION DE TEXTE
# ==============================================================

def get_cv_text(cv_path: str) -> str:
    """
    Extrait le texte d'un fichier PDF de CV.
    
    Args:
        cv_path: Chemin du fichier PDF
    
    Returns:
        Texte extrait du CV, ou chaîne vide en cas d'erreur
    """
    try:
        # Utiliser la fonction d'extraction existante
        from app.services.cv_extraction import extract_text_from_pdf
        return extract_text_from_pdf(cv_path)
    except ImportError:
        # Fallback si le module n'existe pas
        print("⚠️ Module cv_extraction non trouvé")
        return ""
    except Exception as e:
        print(f"❌ Erreur extraction CV: {e}")
        return ""


def get_cv_text_by_name(filename: str) -> str:
    """
    Extrait le texte d'un CV à partir de son nom de fichier.
    
    Args:
        filename: Nom du fichier CV
    
    Returns:
        Texte extrait du CV
    """
    try:
        cv_path = get_cv_path(filename)
        return get_cv_text(cv_path)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return ""