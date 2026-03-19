Agent de Candidature IA
Automatisation complète du processus de candidature grâce à un agent IA : récupération d’offres, analyse du CV, matching intelligent, optimisation du CV, génération de lettre de motivation et création d’un pack de candidature complet.

🚀 Fonctionnalités principales
Récupération automatique d’offres via API (Adzuna)

Analyse IA du CV (extraction + compréhension)

Analyse IA des offres

Matching CV ↔ Offre avec score

Optimisation du CV pour chaque offre

Génération automatique de lettre de motivation

Création d’un ApplicationPack complet

Dashboard Streamlit pour visualiser et gérer les candidatures

Automatisation via APScheduler (tous les X jours)

🏗️ Architecture du projet
Code
agent_job_search/
│
├── app/                     # Backend FastAPI
│   ├── main.py              # Entrée API
│   ├── scheduler.py         # Tâches automatiques
│   │
│   ├── models/              # Modèles Pydantic
│   │   └── application.py
│   │
│   ├── services/            # Logique métier + IA
│   │   ├── adzuna_api.py
│   │   ├── job_search.py
│   │   ├── ai_agent.py
│   │   ├── cv_extraction.py
│   │   ├── application_builder.py
│   │   ├── application_pipeline.py
│   │   └── application_storage.py
│   │
│   └── routers/             # Endpoints FastAPI
│       ├── jobs.py
│       ├── analyze.py
│       └── profile.py
│
├── dashboard/               # Interface Streamlit
│   ├── dashboard.py
│   └── pages/
│       ├── 1_Offres.py
│       └── 2_Agent_de_Candidature.py
│
├── data/                    # Ressources utilisateur
│   └── cv.pdf
│
├── job_offers.json          # Offres analysées
├── application_packs.json   # Candidatures générées
└── requirements.txt
⚙️ Installation
1. Cloner le dépôt
Code
git clone https://github.com/kove35/agent_job_search.git
cd agent_job_search
2. Créer un environnement virtuel
Code
python -m venv .venv
3. Activer l’environnement
Windows :

Code
.\.venv\Scripts\activate
4. Installer les dépendances
Code
pip install -r requirements.txt
▶️ Lancement du projet
Lancer le backend FastAPI
Code
uvicorn app.main:app --reload
API disponible sur :

Code
http://127.0.0.1:8000
Documentation interactive :

Code
http://127.0.0.1:8000/docs
Lancer le dashboard Streamlit
Code
streamlit run dashboard/dashboard.py
Interface disponible sur :

Code
http://localhost:8501
🤖 Automatisation (APScheduler)
Deux tâches automatiques sont exécutées :

1. Récupération des offres
Appel API Adzuna

Normalisation

Sauvegarde dans job_offers.json

2. Génération des packs de candidature
Analyse CV

Analyse offre

Matching

Optimisation CV

Lettre de motivation

Sauvegarde dans application_packs.json

📦 ApplicationPack (structure)
json
{
  "offer_id": "12345",
  "offer_title": "Data Analyst",
  "company": "TechCorp",
  "location": "Paris",
  "match_score": 82,
  "cv_version_path": null,
  "cover_letter": "...",
  "url": "https://...",
  "created_at": "2026-03-19T10:00:00",
  "status": "pending"
}
🧪 Tests (à venir)
Tests unitaires pour les services IA

Tests d’intégration pour le pipeline

Tests API via pytest + httpx

📈 Roadmap
[ ] Migration JSON → SQLite

[ ] Export PDF du pack de candidature

[ ] Interface web complète (FastAPI + React)

[ ] Multi-CV

[ ] Multi-utilisateurs

[ ] Logs structurés + monitoring

[ ] Cache IA + budget IA

🤝 Contribution
Fork du projet

Création d’une branche :

Code
git checkout -b feature/ma-fonctionnalite
Commit clair :

Code
git commit -m "Ajout : nouvelle fonctionnalité"
Push :

Code
git push origin feature/ma-fonctionnalite
Pull Request

📄 Licence
Projet privé — non destiné à un usage commercial sans autorisation.
