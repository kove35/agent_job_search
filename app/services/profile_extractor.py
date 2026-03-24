# =========================================================
# 🧠 PROFILE EXTRACTOR (IA SERVICE)
# =========================================================
# 🎯 RÔLE :
# Transformer un CV brut (texte) en PROFIL STRUCTURÉ
#
# 👉 C’est le cerveau de ton système de matching
#
# 🔁 UTILISATION DANS TON APP :
# autonomous_agent → extract_profile_from_cv()
#
# 📍 APPELÉ DANS :
# app/agents/autonomous_agent.py
#
# 🔥 FLOW :
# PDF → file_parser → texte CV
#       ↓
# profile_extractor (IA)
#       ↓
# profil structuré (UserProfile)
#       ↓
# scoring → matching → applications
#
# =========================================================


# =========================================================
# 🔹 IMPORTS
# =========================================================
from dotenv import load_dotenv
import os
from openai import OpenAI
from app.models.profile import UserProfile
import json
import re

# 🔥 Chargement des variables d’environnement (.env)
load_dotenv(dotenv_path=".env")

# 🔍 DEBUG (à désactiver en prod)
print("DEBUG API KEY =", os.getenv("OPENAI_API_KEY"))

# 🔑 Client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================================================
# 🔹 PARSE JSON ROBUSTE (AJOUT CRITIQUE)
# =========================================================
def safe_json_parse(content: str):
    """
    Nettoie la réponse GPT et extrait un JSON valide
    """

    try:
        content = content.strip()

        # supprime ```json
        if content.startswith("```"):
            parts = content.split("```")
            if len(parts) > 1:
                content = parts[1]

                if content.startswith("json"):
                    content = content[4:]

        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            raise ValueError("No JSON found")

        return json.loads(match.group())

    except Exception as e:
        raise ValueError(f"JSON parsing failed: {e}")


# =========================================================
# 🔹 EXTRACTION PROFIL
# =========================================================
def extract_profile_from_cv(cv_text: str) -> UserProfile:
    """
    🎯 RÔLE :
    Convertir un CV texte en objet UserProfile

    INPUT :
    - cv_text : texte brut du CV

    OUTPUT :
    - UserProfile (objet structuré utilisé par le scoring)
    """

    try:
        # =====================================================
        # CALL OPENAI
        # =====================================================
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": """
You are an expert HR AI.

Extract structured information from a CV.

Return ONLY JSON with:
- skills (list)
- job_targets (list)
- experience_level (junior, mid, senior)
- locations (list)
- remote_only (true/false)

Be precise and realistic.
"""
                },
                {
                    "role": "user",
                    "content": cv_text
                }
            ]
        )

        content = response.choices[0].message.content

        # 🔍 DEBUG
        # print("RAW GPT:", content)

        # =====================================================
        # PARSE ROBUSTE (IMPORTANT 🔥)
        # =====================================================
        data = safe_json_parse(content)

        # =====================================================
        # CONSTRUCTION OBJET
        # =====================================================
        profile = UserProfile(
            skills=data.get("skills", []),
            job_targets=data.get("job_targets", []),
            experience_level=data.get("experience_level", "junior"),
            locations=data.get("locations", []),
            remote_only=data.get("remote_only", False),
            salary_min=0,
            avoid_keywords=[]
        )

        print("🧠 PROFILE BUILT:", profile)

        return profile

    except Exception as e:
        print("❌ Profile extraction error:", e)

        # 🔁 fallback sécurisé
        return UserProfile(
            skills=[],
            job_targets=[],
            experience_level="junior",
            locations=[],
            remote_only=False,
            salary_min=0,
            avoid_keywords=[]
        )