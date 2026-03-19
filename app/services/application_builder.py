import json
from datetime import datetime
from app.models.application import ApplicationPack
from app.services.application_storage import load_application_packs, save_application_packs
from app.services.ai_agent import (
    analyze_offer,
    analyze_cv,
    match_cv_offer,
    optimize_cv_for_offer,
    auto_apply,
    clean_cv_text
)
from app.services.cv_extraction import extract_text_from_pdf


def build_application_pack(offer: dict, cv_pdf_path: str) -> ApplicationPack:
    """
    Pipeline complet :
    - extraction CV
    - analyse CV
    - analyse offre
    - matching
    - optimisation CV
    - lettre de motivation
    - création ApplicationPack
    """

    # 1) Extraire le texte du CV PDF
    raw_cv_text = extract_text_from_pdf(cv_pdf_path)
    cv_text = clean_cv_text(raw_cv_text)

    # 2) Analyse du CV
    cv_analysis = analyze_cv(cv_text)["analysis"]

    # 3) Analyse de l'offre
    offer_analysis = analyze_offer(offer)["analysis"]

    # 4) Matching
    match_result = match_cv_offer(cv_analysis, offer_analysis)["match"]

    # 5) CV optimisé
    optimized_cv = optimize_cv_for_offer(cv_analysis, offer_analysis, match_result)["optimized_cv"]

    # 6) Lettre de motivation (via auto_apply)
    auto = auto_apply(cv_text, offer)
    cover_letter = json.loads(auto["auto_apply"])["cover_letter"]

    # 7) Score final
    match_score = json.loads(match_result)["matching_score"]

    # 8) Création du pack
    pack = ApplicationPack(
        offer_id=offer.get("id", ""),
        offer_title=offer.get("title", ""),
        company=offer.get("company", ""),
        location=offer.get("location"),
        match_score=match_score,
        cv_version_path=None,  # génération PDF plus tard
        cover_letter=cover_letter,
        url=offer.get("url"),
        created_at=datetime.utcnow().isoformat(),
        status="pending"
    )

    # 9) Sauvegarde
    packs = load_application_packs()
    packs.append(pack)
    save_application_packs(packs)

    return pack
