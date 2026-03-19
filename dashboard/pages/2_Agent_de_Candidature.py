import streamlit as st
import json
from app.services.application_storage import load_application_packs, save_application_packs
from app.models.application import ApplicationPack


st.set_page_config(page_title="Agent de Candidature IA", layout="wide")

st.title("🤖 Agent de Candidature IA")
st.write("Voici les candidatures générées automatiquement par ton agent IA.")


# ---------------------------------------------------------
# Charger les packs
# ---------------------------------------------------------
packs = load_application_packs()

if not packs:
    st.warning("Aucune candidature générée pour le moment.")
    st.stop()


# ---------------------------------------------------------
# Tri par score
# ---------------------------------------------------------
packs_sorted = sorted(packs, key=lambda p: p.match_score, reverse=True)

st.subheader("📊 Candidatures classées par score de matching")


# ---------------------------------------------------------
# Affichage des packs
# ---------------------------------------------------------
for pack in packs_sorted:
    with st.expander(f"🎯 {pack.offer_title} — {pack.company} ({pack.match_score}%)"):

        st.markdown(f"**📍 Lieu :** {pack.location}")
        st.markdown(f"**🔗 Offre :** [Voir l'offre]({pack.url})")
        st.markdown(f"**📅 Généré le :** {pack.created_at}")
        st.markdown(f"**📌 Statut :** `{pack.status}`")

        st.divider()

        # Lettre de motivation
        st.markdown("### 📝 Lettre de motivation générée")
        st.text_area("Lettre de motivation", pack.cover_letter, height=250)

        st.divider()

        # CV optimisé (texte)
        st.markdown("### 📄 CV optimisé (texte brut)")
        if pack.cv_version_path:
            st.success(f"CV optimisé disponible : {pack.cv_version_path}")
        else:
            st.info("Le CV optimisé n'est pas encore généré en PDF.")

        st.divider()

        # Bouton : marquer comme envoyée
        if st.button(f"📨 Marquer comme envoyée — {pack.offer_id}"):
            pack.status = "sent"
            save_application_packs(packs)
            st.success("Candidature marquée comme envoyée.")
            st.experimental_rerun()
