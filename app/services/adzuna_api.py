# On importe la bibliothèque qui permet de faire des appels HTTP (API)
import requests

# Typing permet juste d'aider à comprendre les types (liste, dictionnaire…)
from typing import List, Dict, Any

# On importe notre fichier de configuration (config.py)
from app.core.config import settings


# On crée une "erreur personnalisée"
# Ça permet d'avoir des messages plus propres que les erreurs Python classiques
class AdzunaAPIError(Exception):
    pass


# URL de base de l'API Adzuna
# On ne met pas encore la page ici (on l'ajoutera plus tard)
BASE_URL = "https://api.adzuna.com/v1/api/jobs/fr/search"


# Fonction principale pour récupérer les offres
def fetch_adzuna_jobs(
    page: int = 1,                  # numéro de page (1 par défaut)
    query: str | None = None,       # mot-clé (ex : "technicien")
    location: str | None = None,    # lieu (ex : "Rennes")
    results: int | None = None,     # nombre de résultats
) -> List[Dict[str, Any]]:         # la fonction renvoie une liste de dictionnaires

    # ==========================================================
    # 🔑 Vérification des clés API
    # ==========================================================
    if not settings.ADZUNA_APP_ID or not settings.ADZUNA_APP_KEY:
        # Si les clés ne sont pas dans le .env → erreur
        raise AdzunaAPIError("Clés Adzuna manquantes dans .env")

    # ==========================================================
    # 🌍 Construction de l'URL complète
    # ==========================================================
    # Exemple final : https://.../search/1
    url = f"{BASE_URL}/{page}"

    # ==========================================================
    # ⚙️ Paramètres envoyés à l'API
    # ==========================================================
    params = {
        "app_id": settings.ADZUNA_APP_ID,         # clé ID
        "app_key": settings.ADZUNA_APP_KEY,       # clé secrète
        "results_per_page": results or settings.JOB_RESULTS_PER_PAGE,
        "what": query or settings.JOB_KEYWORD,    # métier recherché
        "where": location or settings.JOB_LOCATION, # localisation
        "content-type": "application/json",       # format JSON
    }

    # ==========================================================
    # 📡 Appel API
    # ==========================================================
    try:
        # On envoie une requête HTTP GET à Adzuna
        response = requests.get(url, params=params, timeout=20)

        # Si erreur (ex: 404, 500), Python déclenche une exception
        response.raise_for_status()

        # On transforme la réponse en JSON (dictionnaire Python)
        data = response.json()

        # Vérifie que la clé "results" existe
        if "results" not in data:
            raise AdzunaAPIError("Réponse Adzuna invalide")

        # On renvoie uniquement la liste des offres
        return data["results"]

    # ==========================================================
    # ❌ Gestion des erreurs réseau
    # ==========================================================
    except requests.RequestException as e:
        raise AdzunaAPIError(f"Erreur réseau Adzuna : {e}") from e
        
def fetch_multiple_pages(pages: int = 2) -> List[Dict[str, Any]]:
    # Liste vide pour stocker toutes les offres
    all_jobs = []

    # On boucle sur plusieurs pages
    for page in range(1, pages + 1):
        jobs = fetch_adzuna_jobs(page=page)

        # On ajoute les offres dans la liste
        all_jobs.extend(jobs)

    return all_jobs