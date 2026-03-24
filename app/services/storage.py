# =========================================================
# 📦 APPLICATION STORAGE (DATABASE LAYER)
# =========================================================
# 🧱 RÔLE ARCHITECTURE :
# ---------------------
# Ce module gère UNIQUEMENT l'accès à la base de données
# pour les candidatures.
#
# 👉 Responsabilités :
# - sauvegarder une candidature
# - lire les candidatures
#
# ❌ Ne fait PAS :
# - logique métier IA
# - génération de CV
# - API
#
# 👉 Pattern utilisé :
# DATA ACCESS LAYER (DAL)
#
# =========================================================


# =========================================================
# 🔹 IMPORTS
# =========================================================
from app.db.database import SessionLocal
from app.db.models import Application
from datetime import datetime
import os


# =========================================================
# 📂 DOSSIER STOCKAGE CV
# =========================================================
CV_FOLDER = "storage/cv"

# création dossier si inexistant
os.makedirs(CV_FOLDER, exist_ok=True)


# =========================================================
# 💾 SAVE CV
# =========================================================
def save_cv(filename: str, content: bytes):
    """
    🎯 Sauvegarde un CV sur disque

    INPUT :
    - filename : nom fichier
    - content : contenu binaire

    OUTPUT :
    - filename
    """

    path = os.path.join(CV_FOLDER, filename)

    with open(path, "wb") as f:
        f.write(content)

    return filename


# =========================================================
# 📂 LIST CV
# =========================================================
def list_cvs():
    """
    🎯 Liste les CV disponibles
    """

    return os.listdir(CV_FOLDER)


# =========================================================
# ❌ DELETE CV
# =========================================================
def delete_cv(filename: str):
    """
    🎯 Supprime un CV
    """

    path = os.path.join(CV_FOLDER, filename)

    if os.path.exists(path):
        os.remove(path)


# =========================================================
# 📄 GET PATH CV 🔥 (CE QUI TE MANQUE)
# =========================================================
def get_cv_path(filename: str):
    """
    🎯 Retourne le chemin complet du CV

    🧠 UTILISÉ PAR :
    - agent
    - apply
    - extraction PDF

    EX :
    input  → cv1.pdf
    output → storage/cv/cv1.pdf
    """

    return os.path.join(CV_FOLDER, filename)