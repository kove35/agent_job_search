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
    "location": "Rennes",
    "company": "Entreprise Test"
}

# ---------------------------------------------------------
# Fonction utilitaire pour afficher joliment le JSON
# ---------------------------------------------------------

def pretty(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ---------------------------------------------------------
# TEST : analyse d'offre
# ---------------------------------------------------------

def test_analyze_offer():
    print("\n=== TEST /analyze/offer ===")
    r = requests.post(f"{BASE_URL}/analyze/offer", json=offer_data)
    data = r.json()
    pretty(data)
    return data


# ---------------------------------------------------------
# TEST : analyse de CV
# ---------------------------------------------------------

def test_analyze_cv():
    print("\n=== TEST /analyze/cv ===")
    r = requests.post(f"{BASE_URL}/analyze/cv", json={"text": cv_text})
    data = r.json()
    pretty(data)
    return data


# ---------------------------------------------------------
# TEST : matching CV / offre
# ---------------------------------------------------------

def test_match(cv_analysis, offer_analysis):
    print("\n=== TEST /analyze/match ===")
    payload = {
        "cv": cv_analysis,
        "offer": offer_analysis
    }
    r = requests.post(f"{BASE_URL}/analyze/match", json=payload)
    data = r.json()
    pretty(data)
    return data


# ---------------------------------------------------------
# TEST : optimisation du CV
# ---------------------------------------------------------

def test_optimize_cv(cv_analysis, offer_analysis, match_result):
    print("\n=== TEST /optimize_cv ===")
    payload = {
        "cv": cv_analysis,
        "offer": offer_analysis,
        "match": match_result
    }
    r = requests.post(f"{BASE_URL}/optimize_cv", json=payload)
    data = r.json()
    pretty(data)
    return data


# ---------------------------------------------------------
# TEST : scoring
# ---------------------------------------------------------

def test_score(cv_analysis, offer_analysis):
    print("\n=== TEST /score ===")
    payload = {
        "cv": cv_analysis,
        "offer": offer_analysis
    }
    r = requests.post(f"{BASE_URL}/score", json=payload)
    data = r.json()
    pretty(data)
    return data


# ---------------------------------------------------------
# TEST : pipeline complet auto_apply
# ---------------------------------------------------------

def test_auto_apply():
    print("\n=== TEST /auto_apply ===")
    payload = {
        "cv_text": cv_text,
        "offer": offer_data
    }
    r = requests.post(f"{BASE_URL}/auto_apply", json=payload)
    data = r.json()
    pretty(data)
    return data


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

    print("\n✅ Tests terminés.")