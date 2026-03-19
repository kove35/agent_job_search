# ==========================================================
# IMPORTS
# ==========================================================

# requests permet d'appeler une API sur Internet
import requests

# json permet d'écrire et lire des fichiers JSON
import json

# os permet de manipuler les chemins de fichiers
import os

# On importe la fonction IA qui analyse une offre
from app.services.ai_agent import analyze_offer

# On importe la configuration centralisée
from app.core.config import settings


# ==========================================================
# CLASSE TEMPORAIRE POUR L'IA
# ==========================================================
class OfferObj:
    """
    Transforme un dictionnaire en objet simple.

    Exemple :
    offer["title"]  ->  offer.title
    """

    def __init__(self, data):
        self.title = data.get("title")
        self.description = data.get("description")
        self.location = data.get("location")
        self.company = data.get("company")


# ==========================================================
# FONCTION : récupérer les offres depuis Adzuna
# ==========================================================
def fetch_job_offers(
    what=None,                 # mot-clé recherché
    where=None,                # ville ou zone géographique
    max_pages=1,               # nombre maximum de pages à lire
    results_per_page=3         # nombre d'offres par page
):
    print("🔎 Appel API Adzuna…")

    # Si l'utilisateur ne donne rien,
    # on prend les valeurs par défaut du fichier config.py
    what = what or settings.JOB_KEYWORD
    where = where or settings.JOB_LOCATION

    # Vérifie que les clés API existent
    if not settings.ADZUNA_APP_ID or not settings.ADZUNA_APP_KEY:
        print("❌ Clé API Adzuna manquante dans .env")
        return []

    # URL de base Adzuna
    base_url = "https://api.adzuna.com/v1/api/jobs/fr/search/"

    # Liste vide qui va contenir toutes les offres récupérées
    all_offers = []

    # Boucle sur plusieurs pages
    for page in range(1, max_pages + 1):

        # Paramètres envoyés à l'API
        params = {
            "app_id": settings.ADZUNA_APP_ID,
            "app_key": settings.ADZUNA_APP_KEY,
            "results_per_page": results_per_page,
            "what": what,
            "where": where,
            "content-type": "application/json"
        }

        # Construction de l'URL complète avec la page
        url = f"{base_url}{page}"
        print(f"➡️  Page {page} : {url}")

        try:
            # Appel HTTP GET à l'API
            response = requests.get(url, params=params, timeout=20)

            # Affiche le code de retour HTTP (200, 403, etc.)
            print("➡️  Status code :", response.status_code)

            # Si 403 = problème d'authentification
            if response.status_code == 403:
                print("❌ AUTH_FAIL : clé API invalide ou supprimée")
                return []

            # Déclenche une erreur si le statut HTTP est mauvais
            response.raise_for_status()

            # Transforme la réponse JSON en dictionnaire Python
            data = response.json()

        except Exception as e:
            # En cas d'erreur, on affiche le problème
            print("❌ Erreur API Adzuna :", e)

            # On passe à la page suivante
            continue

        # Récupère la liste des offres
        offers = data.get("results", [])
        print(f"📌 {len(offers)} offres trouvées sur cette page.")

        # Ajoute les offres de cette page à la liste globale
        all_offers.extend(offers)

        # Si le nombre d'offres est inférieur au maximum demandé,
        # cela veut souvent dire qu'il n'y a plus d'autres pages utiles
        if len(offers) < results_per_page:
            break

    # ---------------------------------------------------------
    # FALLBACK : si aucune offre trouvée avec les filtres
    # ---------------------------------------------------------
    if not all_offers:
        print("⚠️ Aucun résultat avec les filtres. Tentative sans filtres…")

        try:
            fallback_url = f"{base_url}1"
            fallback_params = {
                "app_id": settings.ADZUNA_APP_ID,
                "app_key": settings.ADZUNA_APP_KEY,
                "results_per_page": results_per_page
            }

            fallback_response = requests.get(fallback_url, params=fallback_params, timeout=20)
            fallback_response.raise_for_status()
            fallback_data = fallback_response.json()

            all_offers = fallback_data.get("results", [])
            print(f"📌 Fallback : {len(all_offers)} offres trouvées.")

        except Exception as e:
            print("❌ Erreur fallback :", e)

    print(f"🎯 Total : {len(all_offers)} offres récupérées.")
    return all_offers


# ==========================================================
# FONCTION : normaliser une offre brute Adzuna
# ==========================================================
def normalize_offer(item):
    """
    Garde seulement les champs utiles de l'offre Adzuna.
    """
    return {
        "title": item.get("title"),
        "company": item.get("company", {}).get("display_name"),
        "location": item.get("location", {}).get("display_name"),
        "description": item.get("description"),
        "url": item.get("redirect_url")
    }


# ==========================================================
# FONCTION : récupérer, analyser et stocker les offres
# ==========================================================
def fetch_and_store_job_offers(
    max_pages=1,
    results_per_page=3
):
    """
    Pipeline complet :
    1. récupère les offres Adzuna
    2. normalise les données
    3. analyse chaque offre avec l'IA
    4. sauvegarde le tout dans job_offers.json
    """

    print("🔍 Recherche automatique d'offres…")

    # On récupère les offres brutes depuis Adzuna
    offers_raw = fetch_job_offers(
        max_pages=max_pages,
        results_per_page=results_per_page
    )

    # Liste qui contiendra les offres + leur analyse IA
    analyzed_offers = []

    # On boucle sur chaque offre brute
    for item in offers_raw:

        # Normalisation
        offer = normalize_offer(item)

        # Analyse IA
        analysis = analyze_offer(OfferObj(offer))

        # On stocke ensemble :
        # - l'offre nettoyée
        # - le résultat de l'analyse IA
        analyzed_offers.append({
            "offer": offer,
            "analysis": analysis
        })

    # On enregistre le résultat final dans le fichier défini dans config.py
    with open(settings.JOB_OFFERS_PATH, "w", encoding="utf-8") as f:
        json.dump(analyzed_offers, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(analyzed_offers)} offres analysées et stockées.")


# Petit message de debug quand le fichier est exécuté
print(">>> fetch_and_store_job_offers() START")