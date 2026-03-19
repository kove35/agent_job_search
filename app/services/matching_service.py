from openai import OpenAI
import json
import re

client = OpenAI()


def extract_skills(text: str):
    """
    Extrait les compétences depuis un texte (CV ou offre)
    Version robuste (production ready)
    """

    try:
        # -----------------------------------------------------
        # 🔹 prompt amélioré (très important)
        # -----------------------------------------------------
        prompt = f"""
        Tu es un expert RH.

        Analyse le texte suivant et extrait UNIQUEMENT les compétences techniques.

        Texte :
        {text}

        IMPORTANT :
        - Réponds uniquement avec une liste JSON
        - Pas de texte autour
        - Format exact :
        ["Python", "SQL", "Excel"]
        """

        # -----------------------------------------------------
        # 🔹 appel OpenAI
        # -----------------------------------------------------
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # -----------------------------------------------------
        # 🔹 nettoyage (très important)
        # -----------------------------------------------------
        # enlever texte avant/après JSON
        match = re.search(r"\[.*\]", content, re.DOTALL)

        if match:
            json_text = match.group()
        else:
            json_text = content

        # -----------------------------------------------------
        # 🔹 conversion JSON
        # -----------------------------------------------------
        skills = json.loads(json_text)

        # -----------------------------------------------------
        # 🔹 nettoyage final
        # -----------------------------------------------------
        # enlever doublons + normaliser
        skills = list(set([s.strip() for s in skills if isinstance(s, str)]))

        return skills

    except Exception as e:
        print(f"❌ Erreur extract_skills : {e}")
        return []