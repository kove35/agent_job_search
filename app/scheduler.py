from apscheduler.schedulers.background import BackgroundScheduler
from app.services.job_search import fetch_and_store_job_offers
from app.services.application_pipeline import generate_application_packs_for_new_offers

scheduler = BackgroundScheduler()

def start_scheduler():
    # 1) Récupération + analyse des offres
    scheduler.add_job(
        fetch_and_store_job_offers,
        "interval",
        days=2,
        id="fetch_offers"
    )

    # 2) Génération des packs candidature
    scheduler.add_job(
        lambda: generate_application_packs_for_new_offers("data/cv.pdf"),
        "interval",
        days=2,
        id="generate_packs"
    )

    scheduler.start()
