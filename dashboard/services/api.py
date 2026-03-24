import requests

# ==========================================================
# 🌐 CONFIG
# ==========================================================
API_URL = "http://127.0.0.1:8000"


# ==========================================================
# 🔍 RUN AGENT
# ==========================================================
def run_agent(cv_file=None, cv_name=None, max_jobs=10, location=""):
    """
    🎯 Lance l'agent IA

    🧠 ALGO :
    ----------
    1. Construire payload
    2. Ajouter fichier OU cv_name
    3. Envoyer au backend
    4. Retourner résultats

    🧱 ARCHI :
    UI → API → FastAPI → Agent
    """

    files = {}

    data = {
        "max_jobs": max_jobs,
        "location": location,
        "cv_name": cv_name
    }

    # 📄 si upload
    if cv_file:
        files["file"] = (cv_file.name, cv_file, "application/pdf")

    try:
        response = requests.post(
            f"{API_URL}/agent/run",
            files=files,
            data=data
        )

        if response.status_code == 200:
            return response.json()

        return {"error": response.text}

    except Exception as e:
        return {"error": str(e)}


# ==========================================================
# 📩 APPLY TO JOB
# ==========================================================
def apply_to_job(job, cv_name=None):
    """
    🎯 Génère une candidature

    🧠 ALGO :
    ----------
    job + CV →
        backend →
            IA →
                CV + lettre
    """

    data = {
        "cv_name": cv_name
    }

    try:
        response = requests.post(
            f"{API_URL}/agent/apply",
            json=job,
            data=data
        )

        if response.status_code == 200:
            return response.json()

        return {"error": response.text}

    except Exception as e:
        return {"error": str(e)}


# ==========================================================
# 📊 HISTORIQUE
# ==========================================================
def get_applications():
    """
    🎯 Récupère les candidatures
    """

    try:
        response = requests.get(f"{API_URL}/applications")

        if response.status_code == 200:
            return response.json()

        return {"applications": []}

    except Exception:
        return {"applications": []}


# ==========================================================
# 📂 CV MANAGEMENT
# ==========================================================

def get_cvs():
    """
    🎯 Liste des CV disponibles
    """

    try:
        response = requests.get(f"{API_URL}/cv/list")

        if response.status_code == 200:
            return response.json()

        return {"cvs": []}

    except Exception:
        return {"cvs": []}


def upload_cv(file):
    """
    🎯 Upload CV vers backend
    """

    files = {
        "file": (file.name, file, "application/pdf")
    }

    try:
        response = requests.post(
            f"{API_URL}/cv/upload",
            files=files
        )

        if response.status_code == 200:
            return response.json()

        return {"error": response.text}

    except Exception as e:
        return {"error": str(e)}


def delete_cv(filename):
    """
    🎯 Supprime un CV
    """

    try:
        response = requests.post(
            f"{API_URL}/cv/delete",
            data={"filename": filename}
        )

        if response.status_code == 200:
            return response.json()

        return {"error": response.text}

    except Exception as e:
        return {"error": str(e)}