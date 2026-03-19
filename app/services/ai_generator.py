from openai import OpenAI

client = OpenAI()

def generate_cover_letter(job: dict, cv_text: str) -> str:
    """
    Génère une lettre de motivation
    """

    prompt = f"""
    Tu es un expert en recrutement.

    CV :
    {cv_text}

    Offre :
    {job['title']} chez {job['company']}

    Description :
    {job['description']}

    Écris une lettre de motivation personnalisée.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content