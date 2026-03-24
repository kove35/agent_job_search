import streamlit as st
import sys
import os

# Ajouter le dossier parent (agent_job_search) au PYTHONPATH
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Maintenant les imports fonctionnent
from dashboard.services.api import run_agent
from dashboard.components.uploader import upload_section
from dashboard.components.filters import filter_section
from dashboard.components.job_card import display_job


st.title("🔍 Lancer l'agent")

# ==========================================================
# UI
# ==========================================================
cv_file, run_button = upload_section()

min_score, decision_filter, sort_order, max_jobs, location = filter_section() 

# ==========================================================
# LOGIQUE
# ==========================================================
if run_button:

    if cv_file is None:
        st.warning("Upload un CV")

    else:
        with st.spinner("Analyse en cours..."):

            # Appel backend
            results = run_agent(cv_file, max_jobs, location)

        # Gestion erreur
        if "error" in results:
            st.error(results["error"])

        else:
            jobs = results.get("jobs", [])
            st.write("DEBUG RESULTS:", results)
            st.write("DEBUG JOBS:", jobs)

            if not jobs:
                st.warning("Aucun job trouvé")

            else:
                # ================================
                # FILTRE
                # ================================
                jobs = [
                    j for j in jobs
                    if j.get("score", 0) >= min_score
                    and j.get("decision") in decision_filter
                ]

                # ================================
                # TRI
                # ================================
                reverse = "décroissant" in sort_order

                jobs = sorted(
                    jobs,
                    key=lambda x: x.get("score", 0),
                    reverse=reverse
                )

                # ================================
                # KPI
                # ================================
                avg_score = sum(j["score"] for j in jobs) / len(jobs)
                apply_count = len([j for j in jobs if j["decision"] == "APPLY"])

                col1, col2, col3 = st.columns(3)
                col1.metric("Jobs", len(jobs))
                col2.metric("Score moyen", f"{avg_score:.1f}")
                col3.metric("APPLY", apply_count)

                # ================================
                # AFFICHAGE
                # ================================
                for job in jobs:
                    display_job(job)
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    