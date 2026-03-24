# =========================================================
# 🧠 PROFILE BUILDER (IA CORE SERVICE)
# =========================================================
# 🎯 RÔLE :
# Construire un profil utilisateur structuré à partir d’un CV
#
# 👉 Transforme un texte brut en données exploitables :
# - skills
# - job_targets
# - niveau d'expérience
# - préférences
#
# 🔁 UTILISATION DANS TON APP :
# autonomous_agent → generate_profile_from_cv()
#
# 📍 APPELÉ DANS :
# app/agents/autonomous_agent.py
#
# 🔥 FLOW COMPLET :
# CV (PDF → texte) 
#   ↓
# profile_builder (IA OpenAI)
#   ↓
# profil structuré (JSON)
#   ↓
# scoring → matching → applications
#
# =========================================================


# =========================================================
# 🔹 IMPORTS
# =========================================================
from openai import OpenAI
import os
import json
import re

# 🔑 Initialisation client OpenAI (clé via .env)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================================================
# 🔹 PARSING JSON SÉCURISÉ
# =========================================================
def safe_json_parse(content: str):
    """
    🎯 RÔLE :
    Parser une réponse GPT même si elle est mal formatée

    👉 Cas gérés :
    - ```json ... ```
    - texte avant/après JSON
    - JSON incomplet

    OUTPUT :
    - dict JSON ou erreur structurée
    """

    try:
        content = content.strip()

        # 🔥 suppression des blocs markdown
        if content.startswith("```"):
            parts = content.split("```")
            if len(parts) > 1:
                content = parts[1]

                if content.startswith("json"):
                    content = content[4:]

        # 🔥 extraction JSON avec regex
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            return {
                "error": "No JSON found",
                "raw": content[:300]
            }

        json_str = match.group()

        return json.loads(json_str)

    except Exception as e:
        return {
            "error": "Parsing failed",
            "raw": content[:300],
            "details": str(e)
        }


# =========================================================
# 🔹 GÉNÉRATION PROFIL IA
# =========================================================
def generate_profile_from_cv(cv_text: str):
    """
    🎯 RÔLE :
    Générer un profil structuré à partir d’un CV texte

    INPUT :
    - cv_text (str)

    OUTPUT :
    - dict profil structuré

    👉 utilisé dans autonomous_agent
    """

    try:
        # =====================================================
        # PROMPT IA
        # =====================================================
        prompt = f"""
Tu es un expert en recrutement.

Analyse ce CV et génère un profil structuré.

CV :
{cv_text}

FORMAT JSON STRICT :

{{
  "skills": [],
  "job_targets": [],
  "experience_level": "",
  "remote_only": true,
  "locations": [],
  "salary_min": 0,
  "avoid_keywords": []
}}

Règles :
- skills = compétences techniques principales
- job_targets = métiers réalistes
- experience_level = junior / mid / senior
- remote_only = true si profil tech
- locations = villes ou remote
- salary_min = estimation réaliste
- éviter jobs non qualifiés si profil technique

IMPORTANT :
- réponse JSON uniquement
- aucun texte autour
"""

        # =====================================================
        # CALL OPENAI
        # =====================================================
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un expert RH strict."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content

        # 🔍 DEBUG (optionnel)
        # print("🧠 RAW GPT:", content[:300])

        # =====================================================
        # PARSING ROBUSTE
        # =====================================================
        parsed = safe_json_parse(content)

        if "error" in parsed:
            print("❌ PROFILE PARSE ERROR:", parsed)
            return parsed

        # =====================================================
        # VALIDATION + FALLBACK
        # =====================================================
        parsed.setdefault("skills", [])
        parsed.setdefault("job_targets", [])
        parsed.setdefault("experience_level", "unknown")
        parsed.setdefault("remote_only", False)
        parsed.setdefault("locations", [])
        parsed.setdefault("salary_min", 0)
        parsed.setdefault("avoid_keywords", [])

        # 🔍 DEBUG FINAL
        print("🧠 PROFILE BUILT:", parsed)

        return parsed

    except Exception as e:
        print("❌ PROFILE BUILDER ERROR:", e)

        return {
            "error": "Generation failed",
            "details": str(e)
        }