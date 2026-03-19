from openai import OpenAI

client = OpenAI()

def adapt_cv(cv_text: str, job: dict) -> str:
    """
    Adapte le CV au job
    """

    prompt = f"""
    Tu es recruteur.

    CV :
    {cv_text}

    Offre :
    {job['title']} chez {job['company']}

    Description :
    {job['description']}

    Adapte le CV pour ce poste.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content