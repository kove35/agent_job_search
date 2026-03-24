import streamlit as st
from services.api import apply_to_job

st.title("📩 Générer candidature")

job = st.session_state.get("selected_job")

if not job:
    st.warning("Aucune offre sélectionnée")
    st.stop()

# =========================
# INFOS JOB
# =========================
st.subheader("💼 Offre sélectionnée")
st.write(job["title"])
st.write(job["company"])
st.write(job["location"])

# =========================
# ACTION
# =========================
if st.button("🚀 Générer candidature"):

    with st.spinner("Génération IA..."):

        result = apply_to_job(job)

    if "error" in result:
        st.error(result["error"])

    else:
        st.success("Candidature générée")

        # =========================
        # LETTRE
        # =========================
        st.subheader("📩 Lettre de motivation")
        st.write(result.get("cover_letter", ""))

        # =========================
        # CV
        # =========================
        st.subheader("📄 CV optimisé")
        st.write(result.get("cv", ""))