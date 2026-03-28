"""
=====================================================================
📦 STORAGE PACKAGE - POINT D'ENTRÉE UNIQUE
=====================================================================

🎯 RÔLE :
Ce fichier est la "porte d'entrée" pour tous les services de stockage.
Au lieu d'importer depuis plusieurs fichiers, on peut tout importer depuis ici.

📚 POUR UN DÉBUTANT :
C'est comme un standard téléphonique. Tu appelles un seul numéro,
et on te redirige vers le bon service.

Exemple d'utilisation :
    from app.services.storage import save_cv, save_application, get_last_cv

Au lieu de :
    from app.services.storage.cv_storage import save_cv, get_last_cv
    from app.services.storage.application_storage import save_application

=====================================================================
"""

# ==============================================================
# 🔹 CV STORAGE (gestion des fichiers CV)
# ==============================================================
from app.services.storage.cv_storage import (
    # Opérations de base
    save_cv,               # Sauvegarder un CV (avec timestamp et option set_as_last)
    list_cvs,              # Lister tous les CV (triés par date)
    delete_cv,             # Supprimer un CV
    get_cv_path,           # Obtenir le chemin d'un CV
    get_cv_info,           # Obtenir les infos d'un CV (taille, date)
    
    # ✅ Gestion du dernier CV utilisé
    save_last_cv,          # Sauvegarder le nom du dernier CV utilisé
    get_last_cv,           # Récupérer le nom du dernier CV utilisé
    clear_last_cv,         # Effacer la référence du dernier CV
    update_last_cv,        # Mettre à jour le dernier CV (sans upload)
    get_default_cv         # Obtenir le CV par défaut (dernier ou plus récent)
)

# ==============================================================
# 🔹 APPLICATION STORAGE (gestion des candidatures en DB)
# ==============================================================
from app.services.storage.application_storage import (
    save_application,                 # Créer une candidature
    get_applications,                 # Lister les candidatures
    get_application_by_id,            # Trouver une candidature par ID
    get_applications_by_job_id,       # Trouver les candidatures d'une offre
    update_application_status,        # Changer le statut
    delete_application,               # Supprimer une candidature
    get_applications_stats            # Statistiques
)

# ==============================================================
# 🔹 RÉTROCOMPATIBILITÉ (pour les anciens imports)
# ==============================================================
# 📚 POUR UN DÉBUTANT :
# Certains fichiers utilisent encore l'ancien nom "save_application_pack".
# Cette ligne crée un ALIAS : save_application_pack = save_application
# Ainsi, le code existant continue de fonctionner sans modification.
save_application_pack = save_application

# ==============================================================
# 🔹 EXPORTS (ce qui est accessible depuis l'extérieur)
# ==============================================================
__all__ = [
    # CV storage - Opérations de base
    "save_cv",
    "list_cvs",
    "delete_cv",
    "get_cv_path",
    "get_cv_info",
    
    # CV storage - Gestion du dernier CV (✅ NOUVEAU)
    "save_last_cv",
    "get_last_cv",
    "clear_last_cv",
    "update_last_cv",
    "get_default_cv",

    # Application storage
    "save_application",
    "get_applications",
    "get_application_by_id",
    "get_applications_by_job_id",
    "update_application_status",
    "delete_application",
    "get_applications_stats",

    # Rétrocompatibilité
    "save_application_pack"
]