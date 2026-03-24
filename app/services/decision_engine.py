# =========================================================
# 🎯 DECISION ENGINE (BUSINESS LOGIC)
# =========================================================
# 🎯 RÔLE :
# Décider quoi faire avec un job :
# - APPLY (postuler)
# - REVIEW (vérifier)
# - SKIP (ignorer)
#
# 👉 basé sur score 0 → 100
#
# =========================================================


def decide(score: float) -> str:
    """
    Prend un score (0 → 100)
    retourne une décision métier
    """

    if score >= 70:
        return "APPLY"

    elif score >= 50:
        return "REVIEW"

    return "SKIP"