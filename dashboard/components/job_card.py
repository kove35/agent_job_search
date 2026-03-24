import streamlit as st

def display_job(job):
    """
    Affiche un job sous forme de carte UI
    """

    # Récupération des infos
    title = job.get("title", "N/A")
    company = job.get("company", "N/A")
    score = job.get("score", 0)
    decision = job.get("decision", "UNKNOWN")

    # ======================================================
    # BADGE SCORE
    # ======================================================
    if score >= 80:
        badge = "🔥 HIGH"
        color = "green"
    elif score >= 60:
        badge = "⚡ MEDIUM"
        color = "orange"
    else:
        badge = "❌ LOW"
        color = "red"

    decision_color = "green" if decision == "APPLY" else "red"

    # ======================================================
    # AFFICHAGE
    # ======================================================
    with st.container():

        col1, col2 = st.columns([3, 1])

        # Partie gauche
        with col1:
            st.markdown(f"### 💼 {title}")
            st.write(f"🏢 {company}")
            st.markdown(f":{color}[{badge}]")

        # Partie droite
        with col2:
            st.metric("Score", f"{score}%")
            st.markdown(f":{decision_color}[{decision}]")

        # Barre de progression
        st.progress(score / 100)

        # Lettre de motivation
        if "cover_letter" in job:
            with st.expander("📩 Lettre de motivation"):
                st.write(job["cover_letter"])

        st.divider()
    if st.button(f"Postuler à {title}", key=f"apply_{title}"):
        st.session_state["selected_job"] = job