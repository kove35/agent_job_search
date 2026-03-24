import streamlit as st
from dashboard.services.api import get_cvs, upload_cv, delete_cv

def upload_section():
    """
    UI Upload CV simple
    """

    st.subheader("📄 Upload ton CV")

    cv_file = st.file_uploader(
        "Dépose ton CV (PDF uniquement)",
        type=["pdf"]
    )

    run_button = st.button("🚀 Lancer l'agent")

    return cv_file, run_button