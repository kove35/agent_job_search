# =========================================================
# 📦 APPLICATION BUILDER (CORE PIPELINE IA)
# =========================================================

import json
from datetime import datetime

from app.models.application import ApplicationPack

from app.services.ai_agent import (
    analyze_offer,
    analyze_cv,
    match_cv_offer,
    optimize_cv_for_offer,
    auto_apply,
    clean_cv_text
)

from app.services.cv_extraction import extract_text_from_pdf
from app.services.pdf_generator import generate_pdf


# =========================================================
# 🔹 SAFE JSON PARSE
# =========================================================
def safe_json_parse(data):
    """
    🎯 Sécurise les réponses IA
    """
    try:
        if isinstance(data, dict):
            return data

        return json.loads(data)

    except Exception:
        return {}


# =========================================================
# 🔹 NORMALISATION TEXTE (🔥 IMPORTANT)
# =========================================================
def ensure_text(data):
    """
    🎯 Garantit un string exploitable

    🧠 PROBLÈME :
    IA peut renvoyer :
    - dict ❌
    - string JSON ❌
    - string OK ✅

    🧠 SOLUTION :
    → toujours convertir en string propre
    """

    if isinstance(data, dict):
        return json.dumps(data, indent=2)

    if data is None:
        return ""

    return str(data)


# =========================================================
# 🔹 BUILD APPLICATION PACK
# =========================================================
def build_application_pack(offer: dict, cv_pdf_path: str) -> ApplicationPack:

    print(f"🧠 BUILD PACK : {offer.get('title')}")

    # =====================================================
    # 1️⃣ EXTRACTION CV
    # =====================================================
    raw_cv_text = extract_text_from_pdf(cv_pdf_path)

    if not raw_cv_text:
        print("❌ CV vide")
        return None

    cv_text = clean_cv_text(raw_cv_text)

    # =====================================================
    # 2️⃣ ANALYSE CV
    # =====================================================
    cv_analysis_raw = analyze_cv(cv_text)
    cv_analysis = safe_json_parse(cv_analysis_raw).get("analysis", {})

    # =====================================================
    # 3️⃣ ANALYSE OFFRE
    # =====================================================
    offer_analysis_raw = analyze_offer(offer)
    offer_analysis = safe_json_parse(offer_analysis_raw).get("analysis", {})

    # =====================================================
    # 4️⃣ MATCHING
    # =====================================================
    match_raw = match_cv_offer(cv_analysis, offer_analysis)
    match_data = safe_json_parse(match_raw).get("match", {})

    match_score = match_data.get("matching_score", 0)

    # =====================================================
    # 5️⃣ OPTIMISATION CV
    # =====================================================
    optimized_cv_raw = optimize_cv_for_offer(
        cv_analysis,
        offer_analysis,
        match_data
    )

    optimized_cv = safe_json_parse(optimized_cv_raw).get("optimized_cv", "")

    # =====================================================
    # 6️⃣ LETTRE
    # =====================================================
    auto_raw = auto_apply(cv_text, offer)
    auto_data = safe_json_parse(auto_raw).get("auto_apply", {})

    cover_letter = auto_data.get("cover_letter", "")

    # =====================================================
    # 🔥 NORMALISATION (CORRECTION BUG)
    # =====================================================
    optimized_cv = ensure_text(optimized_cv)
    cover_letter = ensure_text(cover_letter)

    # =====================================================
    # 📄 GÉNÉRATION PDF
    # =====================================================
    cv_pdf = generate_pdf(optimized_cv, "cv")
    letter_pdf = generate_pdf(cover_letter, "letter")

    # =====================================================
    # 📦 PACK FINAL
    # =====================================================
    pack = ApplicationPack(
        offer_id=str(offer.get("id", "")),
        offer_title=offer.get("title", ""),
        company=offer.get("company", ""),
        location=offer.get("location"),
        match_score=match_score,

        cv_version_path=cv_pdf,
        cover_letter=cover_letter,

        url=offer.get("url"),
        created_at=datetime.utcnow().isoformat(),
        status="pending"
    )

    # 🔥 attribut dynamique (non DB)
    pack.letter_pdf = letter_pdf

    print(f"✅ PACK OK (score={match_score})")

    return pack