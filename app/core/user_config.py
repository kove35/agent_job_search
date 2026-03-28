"""
📦 USER CONFIG
==============
Fichier de configuration STATIQUE avec les coordonnées de l'utilisateur.
Ces données sont utilisées UNIQUEMENT pour :
- Lettres de motivation
- En-têtes de candidature
- Coordonnées de contact

⚠️ À NE PAS CONFONDRE AVEC :
- UserProfile (extrait du CV pour le matching)
- locations (localisations souhaitées pour le travail)
"""

# =========================================================
# 📝 COORDONNÉES UTILISATEUR
# =========================================================
USER_CONFIG = {
    "name": "Paterne Gankama",
    "address": "24 Square des Collines\n35000 Rennes\nFrance",
    "email": "p.gankama@gmail.com",
    "phone": "06 41 38 92 88",
    "website": "",  # Optionnel
    "linkedin": "",  # Optionnel
    "github": ""     # Optionnel
}


# =========================================================
# 🔧 FONCTIONS D'ACCÈS
# =========================================================
def get_user_name() -> str:
    """Retourne le nom de l'utilisateur"""
    return USER_CONFIG.get("name", "")


def get_user_address() -> str:
    """Retourne l'adresse postale"""
    return USER_CONFIG.get("address", "")


def get_user_email() -> str:
    """Retourne l'email"""
    return USER_CONFIG.get("email", "")


def get_user_phone() -> str:
    """Retourne le téléphone"""
    return USER_CONFIG.get("phone", "")


def get_user_contact() -> dict:
    """Retourne toutes les coordonnées"""
    return {
        "name": USER_CONFIG.get("name", ""),
        "address": USER_CONFIG.get("address", ""),
        "email": USER_CONFIG.get("email", ""),
        "phone": USER_CONFIG.get("phone", ""),
        "website": USER_CONFIG.get("website", ""),
        "linkedin": USER_CONFIG.get("linkedin", ""),
        "github": USER_CONFIG.get("github", "")
    }


def format_address_for_letter() -> str:
    """Formate l'adresse pour une lettre de motivation"""
    address = USER_CONFIG.get("address", "")
    # Remplacer les \n par des sauts de ligne HTML si besoin
    return address.replace("\n", "<br>") if address else ""