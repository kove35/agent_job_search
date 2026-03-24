# =========================
# IMPORTS
# =========================
import requests

from app.services.ai_agent import analyze_offer
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import Job


# =========================
# ADAPTATEUR
# =========================
class OfferObj:
    def __init__(self, data):
        self.title = data.get("title")
        self.description = data.get("description")
        self.location = data.get("location")
        self.company = data.get("company")


# =========================
# FETCH
# =========================
def fetch_job_offers(max_pages=1, results_per_page=5):

    base_url = "https://api.adzuna.com/v1/api/jobs/fr/search/"
    all_offers = []

    for page in range(1, max_pages + 1):

        url = f"{base_url}{page}"

        params = {
            "app_id": settings.ADZUNA_APP_ID,
            "app_key": settings.ADZUNA_APP_KEY,
            "results_per_page": results_per_page,
            "what": settings.JOB_KEYWORD,
            "where": settings.JOB_LOCATION
        }

        response = requests.get(url, params=params)
        data = response.json()

        offers = data.get("results", [])
        all_offers.extend(offers)

    return all_offers


# =========================
# NORMALIZE
# =========================
def normalize_offer(item):
    return {
        "title": item.get("title"),
        "company": item.get("company", {}).get("display_name"),
        "location": item.get("location", {}).get("display_name"),
        "description": item.get("description"),
    }


# =========================
# PIPELINE
# =========================
def fetch_and_store_job_offers(max_pages=1, results_per_page=5):

    print("🚀 PIPELINE START")

    raw_offers = fetch_job_offers(max_pages, results_per_page)

    analyzed_jobs = []

    for item in raw_offers:
        try:
            offer = normalize_offer(item)

            print(f"🔍 Analyse : {offer.get('title')}")

            analysis = analyze_offer(OfferObj(offer))

            analyzed_jobs.append({
                "offer": offer,
                "analysis": analysis
            })

        except Exception as e:
            print("❌ Erreur analyse :", e)

    # =========================
    # SAVE DB
    # =========================
    db = SessionLocal()
    saved_count = 0

    for job_data in analyzed_jobs:

        offer = job_data["offer"]

        exists = db.query(Job).filter(
            Job.title == offer.get("title"),
            Job.company == offer.get("company")
        ).first()

        if exists:
            continue

        job = Job(
            title=offer.get("title"),
            company=offer.get("company"),
            location=offer.get("location"),
            description=offer.get("description")
        )

        db.add(job)
        saved_count += 1

    db.commit()
    db.close()

    print(f"✅ {saved_count} jobs sauvegardés en DB")

    return analyzed_jobs