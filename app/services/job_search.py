import requests
import json
import os
from app.services.ai_agent import analyze_offer

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")


# ---------------------------------------------------------
# 🔥 VERSION OPTIMALE DE fetch_job_offers()
# ---------------------------------------------------------
def fetch_job_offers(
    what="technicien",
    where="Rennes",
    max_pages=3,
    results_per_page=20
):
    print("🔎 Appel API Adzuna…")

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("❌ Clé API Adzuna manquante dans .env")
        return []

    base_url = "https://api.adzuna.com/v1/api/jobs/fr/search/"
    all_offers = []

    for page in range(1, max_pages + 1):
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "results_per_page": results_per_page,
            "what": what,
            "where": where,
            "content-type": "application/json"
        }

        url = f"{base_url}{page}"
        print(f"➡️  Page {page} : {url}")

        try:
            response = requests.get(url, params=params)
            print("➡️  Status code :", response.status_code)

            if response.status_code == 403:
                print("❌ AUTH_FAIL : clé API invalide ou supprimée")
                return []

            response.raise_for_status()
            data = response.json()

        except Exception as e:
            print("❌ Erreur API Adzuna :", e)
            continue

        offers = data.get("results", [])
        print(f"📌 {len(offers)} offres trouvées sur cette page.")

        all_offers.extend(offers)

        # Stop si Adzuna n'a plus de résultats
        if len(offers) < results_per_page:
            break

    # Fallback si aucune offre trouvée
    if not all_offers:
        print("⚠️ Aucun résultat avec les filtres. Tentative sans filtres…")

        try:
            fallback_url = f"{base_url}1"
            fallback_params = {
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_APP_KEY,
                "results_per_page": results_per_page
            }

            fallback_response = requests.get(fallback_url, params=fallback_params)
            fallback_response.raise_for_status()
            fallback_data = fallback_response.json()

            all_offers = fallback_data.get("results", [])
            print(f"📌 Fallback : {len(all_offers)} offres trouvées.")

        except Exception as e:
            print("❌ Erreur fallback :", e)

    print(f"🎯 Total : {len(all_offers)} offres récupérées.")
    return all_offers


# ---------------------------------------------------------
# 🔥 fetch_and_store_job_offers() (inchangé, mais optimisé)
# ---------------------------------------------------------
def fetch_and_store_job_offers():
    print("🔍 Recherche automatique d'offres…")

    offers_raw = fetch_job_offers()
    analyzed_offers = []

    for item in offers_raw:

        # Normalisation propre
        offer = {
            "title": item.get("title"),
            "company": item.get("company", {}).get("display_name"),
            "location": item.get("location", {}).get("display_name"),
            "description": item.get("description"),
            "url": item.get("redirect_url")
        }

        # Objet pour l’IA
        class OfferObj:
            def __init__(self, data):
                self.title = data.get("title")
                self.description = data.get("description")
                self.location = data.get("location")
                self.company = data.get("company")

        analysis = analyze_offer(OfferObj(offer))

        analyzed_offers.append({
            "offer": offer,
            "analysis": analysis
        })

    # Stockage local
    with open("job_offers.json", "w", encoding="utf-8") as f:
        json.dump(analyzed_offers, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(analyzed_offers)} offres analysées et stockées.")


print(">>> fetch_and_store_job_offers() START")
