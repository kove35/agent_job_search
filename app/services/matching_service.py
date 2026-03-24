# =========================================================
# 🧩 MATCHING SERVICE (CORE IA)
# =========================================================
# 🎯 RÔLE :
# Fournir toutes les fonctions de matching :
# - skills matching
# - semantic matching
# - embedding matching (IA)
#
# 👉 utilisé par :
# scoring.py → compute_smart_score()
#
# 📍 FLOW :
# profile_extractor → matching → scoring → agent
#
# =========================================================


# =========================================================
# 🔹 IMPORTS
# =========================================================
from openai import OpenAI
import json
import re

from app.services.embedding_service import get_embedding, cosine_similarity

client = OpenAI()


# =========================================================
# 🔹 NORMALISATION (CRITIQUE)
# =========================================================
def normalize_skill(skill: str):
    """
    Nettoie les compétences pour éviter les faux négatifs
    """
    return skill.lower().strip()


# =========================================================
# 🔹 GPT FALLBACK (RARE 🔥)
# =========================================================
def extract_skills_with_gpt(text: str):
    """
    Utilisé UNIQUEMENT si aucune skill n’est fournie
    ⚠️ coûteux → éviter en prod
    """

    try:
        prompt = f"""
Tu es un expert RH.

Analyse le texte et retourne UNIQUEMENT une liste JSON de compétences techniques.

Texte :
{text}

Format :
["Python", "SQL", "Excel"]
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        match = re.search(r"\[.*\]", content, re.DOTALL)
        json_text = match.group() if match else content

        skills = json.loads(json_text)

        return list(set(normalize_skill(s) for s in skills if isinstance(s, str)))

    except Exception as e:
        print(f"❌ GPT fallback error: {e}")
        return []


# =========================================================
# 🔹 EXTRACTION SKILLS (PRIORITÉ DATA EXISTANTE)
# =========================================================
def extract_skills(text: str, existing_skills=None):
    """
    1️⃣ utilise les skills déjà présentes
    2️⃣ sinon fallback GPT
    """

    if existing_skills:
        return list(set(normalize_skill(s) for s in existing_skills))

    return extract_skills_with_gpt(text)


# =========================================================
# 🔹 SKILL MATCH (TRÈS IMPORTANT)
# =========================================================
def compute_skill_match_score(job, profile):
    """
    Compare skills CV vs job

    OUTPUT : score 0 → 100
    """

    # ⚠️ ton job actuel est simple (pas analysis)
    job_skills = job.get("skills", [])

    job_skills = [normalize_skill(s) for s in job_skills]

    profile_skills = [
        normalize_skill(s) for s in profile.get("skills", [])
    ]

    if not profile_skills:
        return 0

    matches = sum(1 for s in profile_skills if s in job_skills)

    return int((matches / len(profile_skills)) * 100)


# =========================================================
# 🔹 SEMANTIC MATCH (RÈGLES SIMPLES)
# =========================================================
def compute_semantic_match(job, profile):
    """
    Matching basé sur texte (titre + description)
    """

    text = (
        (job.get("title", "") or "") + " " +
        (job.get("description", "") or "")
    ).lower()

    score = 0

    for skill in profile.get("skills", []):
        if skill.lower() in text:
            score += 5

    for target in profile.get("job_targets", []):
        if target.lower() in text:
            score += 15

    return score


# =========================================================
# 🔹 EMBEDDING MATCH (IA AVANCÉE)
# =========================================================
def compute_embedding_score(job, profile):
    """
    Matching sémantique via embeddings OpenAI
    """

    job_text = job.get("title", "") + " " + job.get("description", "")
    profile_text = " ".join(profile.get("skills", [])) + " " + " ".join(profile.get("job_targets", []))

    try:
        job_vec = get_embedding(job_text)
        profile_vec = get_embedding(profile_text)

        similarity = cosine_similarity(job_vec, profile_vec)

        return int(similarity * 100)

    except Exception as e:
        print("❌ embedding error:", e)
        return 0