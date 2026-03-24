# =========================================================
# 🧠 EMBEDDING SERVICE (IA CORE)
# =========================================================
# 🎯 RÔLE :
# - transformer du texte en vecteur (embedding)
# - calculer similarité entre job et profil
#
# 👉 utilisé par :
# matching_service → compute_embedding_score()
#
# =========================================================


from openai import OpenAI
import numpy as np
from app.core.config import settings   # 🔥 IMPORTANT

# =========================================================
# 🔹 CLIENT OPENAI
# =========================================================
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# =========================================================
# 🔹 EMBEDDING
# =========================================================
def get_embedding(text: str):
    """
    Génère un vecteur embedding du texte

    👉 utilisé pour similarity AI
    """

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


# =========================================================
# 🔹 SIMILARITÉ COSINUS
# =========================================================
def cosine_similarity(vec1, vec2):
    """
    Compare deux vecteurs
    """

    v1 = np.array(vec1)
    v2 = np.array(vec2)

    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))