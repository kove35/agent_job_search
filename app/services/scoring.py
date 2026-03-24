# =========================================================
# 🎯 SCORING SERVICE (CORE IA)
# =========================================================
# 🎯 RÔLE :
# Calculer un score de compatibilité entre un JOB et un PROFIL
#
# 👉 utilisé pour décider :
# - si on postule
# - classement des jobs
#
# 🔁 UTILISATION :
# autonomous_agent → compute_smart_score()
#
# =========================================================

from app.services.matching_service import compute_embedding_score


def compute_smart_score(job: dict, profile: dict):
    """
    Calcule un score global (0 → 100)
    """

    # =========================
    # NORMALISATION TEXTE
    # =========================
    title = (job.get("title", "") or "").lower()
    description = (job.get("description", "") or "").lower()

    text = title + " " + description

    # =========================
    # INIT
    # =========================
    score = 0

    details = {
        "skills_score": 0,
        "title_score": 0,
        "semantic_score": 0,
        "embedding_score": 0,
        "bonus": [],
        "malus": [],
        "final_score": 0
    }

    # =====================================================
    # 1️⃣ SKILLS MATCH (40 pts)
    # =====================================================
    profile_skills = [s.lower() for s in profile.get("skills", [])]

    match_count = sum(1 for skill in profile_skills if skill in text)

    if profile_skills:
        skills_score = int((match_count / len(profile_skills)) * 40)
    else:
        skills_score = 0

    score += skills_score
    details["skills_score"] = skills_score

    # =====================================================
    # 2️⃣ JOB TARGET MATCH (25 pts)
    # =====================================================
    target_score = 0

    for target in profile.get("job_targets", []):
        if target.lower() in title:
            target_score = 25
            details["bonus"].append(f"+25 target ({target})")
            break

    score += target_score
    details["title_score"] = target_score

    # =====================================================
    # 3️⃣ KEYWORD MATCH (25 pts)
    # =====================================================
    semantic_score = 0

    keywords = profile_skills + profile.get("job_targets", [])

    for word in keywords:
        if word.lower() in description:
            semantic_score += 3

    semantic_score = min(25, semantic_score)

    score += semantic_score
    details["semantic_score"] = semantic_score

    # =====================================================
    # 4️⃣ EMBEDDING MATCH (30 pts)
    # =====================================================
    embedding_score = compute_embedding_score(job, profile)

    embedding_score = int(embedding_score * 0.3)

    score += embedding_score
    details["embedding_score"] = embedding_score

    # =====================================================
    # 5️⃣ BONUS
    # =====================================================
    if "senior" in title:
        score += 5
        details["bonus"].append("+5 senior")

    if "urgent" in description:
        score += 5
        details["bonus"].append("+5 urgent")

    # =====================================================
    # 6️⃣ MALUS
    # =====================================================
    for word in profile.get("avoid_keywords", []):
        if word.lower() in text:
            score -= 30
            details["malus"].append(f"-30 avoid ({word})")

    # =====================================================
    # NORMALISATION
    # =====================================================
    score = max(0, min(100, score))

    details["final_score"] = score

    return score, details