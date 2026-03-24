from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_application(job, cv_text):

    try:
        job = job or {}
        cv = cv_text or ""

        title = job.get("title", "poste")
        company = job.get("company", "entreprise")
        description = job.get("description", "")

        # =========================
        # PROMPTS
        # =========================
        cv_prompt = f"""
Crée un CV professionnel pour :

POSTE : {title}
ENTREPRISE : {company}

DESCRIPTION :
{description}

PROFIL :
{cv}
"""

        letter_prompt = f"""
Rédige une lettre de motivation.

POSTE : {title}
ENTREPRISE : {company}

DESCRIPTION :
{description}

PROFIL :
{cv}
"""

        # =========================
        # CALL CV
        # =========================
        try:
            cv_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": cv_prompt}],
                temperature=0.7
            )
            generated_cv = cv_response.choices[0].message.content
        except Exception as e:
            print(f"❌ CV error: {e}")
            generated_cv = cv  # fallback

        # =========================
        # CALL LETTER
        # =========================
        try:
            letter_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": letter_prompt}],
                temperature=0.7
            )
            cover_letter = letter_response.choices[0].message.content
        except Exception as e:
            print(f"❌ Letter error: {e}")
            cover_letter = "Lettre non générée"

        return {
            "cv": generated_cv,
            "cover_letter": cover_letter
        }

    except Exception as e:
        return {
            "cv": "",
            "cover_letter": "",
            "error": str(e)
        }