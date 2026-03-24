# =========================================================
# ✉️ COVER LETTER GENERATOR (IA SERVICE)
# =========================================================
# 🎯 RÔLE :
# Générer une lettre de motivation personnalisée
#
# 👉 utilisé par :
# application_builder / autonomous_agent
#
# 🔥 OBJECTIF :
# - lettre adaptée au job
# - ton professionnel
# - mots-clés pertinents
#
# =========================================================


# =========================================================
# 🔹 IMPORTS
# =========================================================
from openai import OpenAI

client = OpenAI()


# =========================================================
# 🔹 GENERATE COVER LETTER
# =========================================================
def generate_cover_letter(job: dict, cv_text: str) -> str:
    """
    Génère une lettre de motivation personnalisée

    INPUT :
    - job : dict (title, company, description)
    - cv_text : texte brut du CV

    OUTPUT :
    - lettre de motivation (string)
    """

    try:
        # =========================
        # PROMPT PRO 🔥
        # =========================
        prompt = f"""
Tu es un expert en recrutement.

OBJECTIF :
Rédiger une lettre de motivation courte, percutante et personnalisée.

=========================
CV :
{cv_text}

=========================
OFFRE :
Poste : {job.get('title')}
Entreprise : {job.get('company')}

Description :
{job.get('description')}

=========================
INSTRUCTIONS :

- Lettre structurée :
  1. Accroche
  2. Expérience pertinente
  3. Motivation pour l'entreprise
  4. Conclusion

- Style :
  ✔ professionnel
  ✔ fluide
  ✔ naturel
  ✔ sans répétition

- Longueur :
  ✔ 150 à 250 mots

IMPORTANT :
- Pas d'explication
- Pas de commentaire
- Texte directement utilisable
"""

        # =========================
        # CALL OPENAI
        # =========================
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.4,
            messages=[
                {"role": "system", "content": "Tu es un expert en recrutement."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("❌ Cover letter error:", e)
        return "Lettre non générée."