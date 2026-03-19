import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# ---------------------------------------------------------
# Données de test
# ---------------------------------------------------------

cv_text = """
Technicien de production avec expérience en environnement industriel et microélectronique.
Compétences en supervision, diagnostic, tests, suivi d'indicateurs, ERP, Excel, Power BI.
"""

offer_data = {
    "title": "Technicien de Production Électronique",
    "description": "Supervision, tests, diagnostic, environnement microélectronique, ESD, ERP.",
    "location": "Rennes"
}

# ---------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------

def pretty(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_analyze_offer():
    print("\n=== TEST /analyze ===")
    r = requests.post(f"{BASE_URL}/analyze", json=offer_data)
    pretty(r.json())
    return r.json()["analysis"]

def test_analyze_cv():
    print("\n=== TEST /analyze_cv ===")
    r = requests.post(f"{BASE_URL}/analyze_cv", json={"text": cv_text})
    pretty(r.json())
    return r.json()["analysis"]

def test_match(cv_analysis, offer_analysis):
    print("\n=== TEST /match ===")
    payload = {
        "cv": json.loads(cv_analysis),
        "offer": json.loads(offer_analysis)
    }
    r = requests.post(f"{BASE_URL}/match", json=payload)
    pretty(r.json())
    return r.json()["match"]

def test_optimize_cv(cv_analysis, offer_analysis, match_result):
    print("\n=== TEST /optimize_cv ===")
    payload = {
        "cv": json.loads(cv_analysis),
        "offer": json.loads(offer_analysis),
        "match": json.loads(match_result)
    }
    r = requests.post(f"{BASE_URL}/optimize_cv", json=payload)
    pretty(r.json())
    return r.json()["optimized_cv"]

def test_score(cv_analysis, offer_analysis):
    print("\n=== TEST /score ===")
    payload = {
        "cv": json.loads(cv_analysis),
        "offer": json.loads(offer_analysis)
    }
    r = requests.post(f"{BASE_URL}/score", json=payload)
    pretty(r.json())
    return r.json()["score"]

def test_auto_apply():
    print("\n=== TEST /auto_apply ===")
    payload = {
        "cv_text": cv_text,
        "offer": offer_data
    }
    r = requests.post(f"{BASE_URL}/auto_apply", json=payload)
    pretty(r.json())
    return r.json()["auto_apply"]

def test_job_suggestions():
    print("\n=== TEST /job_suggestions ===")
    r = requests.get(f"{BASE_URL}/job_suggestions")
    pretty(r.json())


# ---------------------------------------------------------
# Pipeline complet
# ---------------------------------------------------------

if __name__ == "__main__":
    print("🚀 Lancement des tests de l'agent IA...\n")

    offer_analysis = test_analyze_offer()
    cv_analysis = test_analyze_cv()

    match_result = test_match(cv_analysis, offer_analysis)
    optimized_cv = test_optimize_cv(cv_analysis, offer_analysis, match_result)
    score = test_score(cv_analysis, offer_analysis)

    auto_apply = test_auto_apply()

    test_job_suggestions()

    print("\n✅ Tests terminés.")
