from app.agents.application_agent import build_application
from app.agents.autonomous_agent import run_autonomous_agent

# =====================================================
# 🔹 FAKE JOB
# =====================================================
job = {
    "title": "Data Analyst Python",
    "company": "TechCorp",
    "description": "Analyse de données, Python, SQL, dashboarding"
}

cv_text = "Python, SQL, data analyse, Power BI, travail en équipe"

# =====================================================
# 🔹 TEST APPLICATION AGENT
# =====================================================
print("\n===== TEST APPLICATION AGENT =====\n")

application = build_application(job, cv_text)

print("CV généré :\n")
print(application["cv"][:300])  # preview

print("\nLettre générée :\n")
print(application["cover_letter"][:300])


# =====================================================
# 🔹 FAKE JOBS LIST
# =====================================================
jobs = [
    {
        "offer": {
            "title": "Data Analyst Python",
            "company": "TechCorp",
            "location": "Paris",
            "description": "Python, SQL, data analyse"
        },
        "analysis": {
            "resume": "Analyse de données",
            "hard_skills": ["Python", "SQL", "Data"]
        }
    },
    {
        "offer": {
            "title": "Employé Polyvalent",
            "company": "McDo",
            "location": "Paris",
            "description": "Service client, restauration"
        },
        "analysis": {
            "resume": "Service client",
            "hard_skills": ["service client"]
        }
    }
]

# =====================================================
# 🔹 TEST AUTONOMOUS AGENT
# =====================================================
print("\n===== TEST AUTONOMOUS AGENT =====\n")

results = run_autonomous_agent(
    jobs=jobs,
    cv_text=cv_text,
    min_score=10,  # 🔥 important pour test
    max_jobs=5
)

for r in results:
    print("\n---------------------------")
    print("Job :", r["job"]["title"])
    print("Score :", r["score"])
    print("Details :", r.get("details"))