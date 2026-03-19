import json
from app.services.application_storage import load_application_packs, save_application_packs
from app.services.application_builder import build_application_pack


def generate_application_packs_for_new_offers(cv_pdf_path: str):
    """
    Pipeline complet :
    - charge les offres déjà analysées (job_offers.json)
    - génère un ApplicationPack pour chaque offre
    - évite les doublons
    - sauvegarde dans application_packs.json
    """

    # Charger les offres déjà analysées
    try:
        with open("job_offers.json", "r", encoding="utf-8") as f:
            offers_data = json.load(f)
    except FileNotFoundError:
        print("❌ Aucun fichier job_offers.json trouvé.")
        return

    # Charger les packs existants
    existing_packs = load_application_packs()
    existing_offer_ids = {p.offer_id for p in existing_packs}

    new_packs = []

    for item in offers_data:
        offer = item["offer"]
        offer_id = offer.get("id", "")

        # Éviter les doublons
        if offer_id in existing_offer_ids:
            continue

        print(f"🧠 Génération du pack pour : {offer.get('title')}")

        pack = build_application_pack(offer, cv_pdf_path)
        new_packs.append(pack)

    # Sauvegarde
    all_packs = existing_packs + new_packs
    save_application_packs(all_packs)

    print(f"✅ {len(new_packs)} nouveaux packs générés.")
