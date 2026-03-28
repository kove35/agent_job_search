# =========================================================
# 📦 APPLICATION PIPELINE (AUTO APPLY CORE)
# =========================================================
# 🧱 RÔLE ARCHITECTURE :
# ---------------------
# Ce module orchestre la génération automatique de candidatures.
#
# 👉 Il NE fait PAS :
# ❌ stockage DB
# ❌ logique IA
#
# 👉 Il FAIT :
# ✔ coordination entre :
#     - offres
#     - builder IA
#     - stockage DB
#
# 👉 Pattern :
# ORCHESTRATION LAYER
#
# =========================================================


# =========================================================
# 🔹 IMPORTS
# =========================================================
import json

# 📦 DB
from app.services.storage.application_storage import get_applications, save_application

# 🤖 IA
from app.services.application_builder import build_application_pack


# =========================================================
# 🔹 PIPELINE PRINCIPAL
# =========================================================
def generate_application_packs_for_new_offers(cv_pdf_path: str):
    """
    🎯 OBJECTIF :
    Générer automatiquement des candidatures pour les nouvelles offres

    INPUT :
    - cv_pdf_path : chemin du CV

    =====================================================
    🧠 ALGORITHME GLOBAL :
    =====================================================

    job_offers.json
        ↓
    charger candidatures existantes (DB)
        ↓
    éviter doublons
        ↓
    générer nouveaux packs (IA)
        ↓
    sauvegarder en DB
    """

    print("🚀 APPLICATION PIPELINE START")

    # =====================================================
    # 1️⃣ LOAD JOB OFFERS (SOURCE)
    # =====================================================
    try:
        with open("job_offers.json", "r", encoding="utf-8") as f:
            offers_data = json.load(f)

        print(f"📦 {len(offers_data)} offres chargées")

    except FileNotFoundError:
        print("❌ job_offers.json introuvable")
        return

    except Exception as e:
        print("❌ Erreur lecture job_offers :", e)
        return

    # =====================================================
    # 2️⃣ LOAD EXISTING APPLICATIONS (DB)
    # =====================================================
    existing_apps = get_applications()

    # ⚠️ sécurité
    if not existing_apps:
        existing_apps = []

    # =====================================================
    # 🧠 ALGO DOUBLONS :
    # on récupère les job_id déjà traités
    # =====================================================
    existing_offer_ids = {
        app.get("job_id") for app in existing_apps
    }

    print(f"📂 {len(existing_offer_ids)} candidatures existantes")

    # =====================================================
    # 3️⃣ GENERATE NEW APPLICATIONS
    # =====================================================
    new_count = 0

    for item in offers_data:

        # 🔥 structure attendue :
        # { "offer": {...} }
        offer = item.get("offer", {})

        # =================================================
        # 🔑 IDENTIFIANT UNIQUE
        # =================================================
        offer_id = offer.get("id") or offer.get("url")

        if not offer_id:
            print("⚠️ Offre sans ID ignorée")
            continue

        # =================================================
        # 🚫 ANTI-DOUBLON
        # =================================================
        if offer_id in existing_offer_ids:
            continue

        print(f"🧠 Génération : {offer.get('title')}")

        try:
            # =================================================
            # 🤖 BUILD PACK (IA)
            # =================================================
            pack = build_application_pack(offer, cv_pdf_path)

            if not pack:
                continue

            # =================================================
            # 💾 SAVE EN DB
            # =================================================
            save_application({
                "job_id": offer_id,
                "title": offer.get("title"),
                "company": offer.get("company"),
                "decision": "AUTO",
                "score": pack.match_score,
                "cover_letter": pack.cover_letter,
                "tailored_cv": pack.cv_version_path
            })

            new_count += 1

        except Exception as e:
            print(f"❌ Erreur build pack : {e}")

    # =====================================================
    # 4️⃣ RESULTAT FINAL
    # =====================================================
    print(f"✅ {new_count} nouvelles candidatures générées")