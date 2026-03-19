def decide(score: float) -> str:
    """
    Décision simple
    """

    if score >= 0.75:
        return "APPLY"
    elif score >= 0.5:
        return "REVIEW"
    return "SKIP"