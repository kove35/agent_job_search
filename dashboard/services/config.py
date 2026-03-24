# ==========================================================
# CONFIGURATION DU BACKEND
# ==========================================================

# URL de ton serveur FastAPI
API_URL = "http://127.0.0.1:8000"

# Endpoint principal (confirmé via /docs)
ENDPOINT_RUN = f"{API_URL}/agent/run"

# Endpoint historique (optionnel)
ENDPOINT_HISTORY = f"{API_URL}/jobs"