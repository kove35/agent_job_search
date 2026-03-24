# =========================================================
# 📄 CV ADAPTER SERVICE (IA GENERATION)
# =========================================================
# 🎯 RÔLE :
# Adapter automatiquement un CV à une offre d'emploi
#
# 👉 utilisé par :
# autonomous_agent → génération candidature
#
# 🔥 FLOW :
# CV brut → adaptation IA → CV optimisé ATS
#
# =========================================================


# =========================================================
# 🔹 IMPORTS
# =========================================================
from openai import OpenAI

client = OpenAI()


# =========================================================
# 🔹 ADAPT CV
# =========================================================
def adapt_cv(cv_text: str, job: dict) -> str:
    """
    Génère un CV optimisé pour une offre

    INPUT :
    - cv_text : texte brut du CV
    - job : dict (title, description, company)

    OUTPUT :
    - CV adapté (texte)
    """

    try:
        # =========================
        # PROMPT PRO (IMPORTANT 🔥)
        # =========================
        prompt = f"""
Tu es un expert RH et ATS.

OBJECTIF :
Adapter ce CV pour maximiser les chances d'embauche.

=========================
CV ORIGINAL :
{cv_text}

=========================
OFFRE :
Poste : {job.get('title')}
Entreprise : {job.get('company')}

Description :
{job.get('description')}

=========================
INSTRUCTIONS :

1. Réécris le CV
2. Mets en avant les compétences pertinentes
3. Ajoute des mots-clés du job
4. Structure propre (ATS friendly)
5. Style professionnel et impactant

IMPORTANT :
- Pas de texte inutile
- Pas d'explication
- Format clair
"""

        # =========================
        # CALL OPENAI
        # =========================
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.3,
            messages=[
                {"role": "system", "content": "Tu es un expert en CV et recrutement."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("❌ CV adaptation error:", e)
        return cv_text  # fallback