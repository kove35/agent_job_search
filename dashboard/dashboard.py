import os
import json
import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# Configuration de la page
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Agent IA Emploi",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard – Agent IA Recherche d'Emploi")
st.write("Visualisation des offres récupérées et analysées automatiquement.")

import requests

st.sidebar.subheader("🔄 Mise à jour des offres")

if st.sidebar.button("Rafraîchir les offres maintenant"):
    with st.spinner("Mise à jour en cours..."):
        try:
            response = requests.get("http://127.0.0.1:8000/refresh_jobs")
            if response.status_code == 200:
                st.success("✔ Offres mises à jour ! Recharge du tableau...")
                st.experimental_rerun()
            else:
                st.error("❌ Erreur lors de la mise à jour.")
        except Exception as e:
            st.error(f"❌ Impossible de contacter le backend : {e}")



# ---------------------------------------------------------
# Chargement robuste du fichier job_offers.json
# ---------------------------------------------------------
def load_data():
    # Chemin absolu vers la racine du projet
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    JSON_PATH = os.path.join(BASE_DIR, "job_offers.json")

    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    except FileNotFoundError:
        st.error(f"❌ Fichier introuvable : {JSON_PATH}")
        return []

    except json.JSONDecodeError:
        st.error("❌ Erreur : fichier JSON corrompu.")
        return []


data = load_data()

if not data:
    st.warning("Aucune donnée disponible. Lance ton agent IA pour générer des offres.")
    st.stop()


# ---------------------------------------------------------
# Normalisation en DataFrame
# ---------------------------------------------------------
offers = []
for item in data:
    offer = item["offer"]
    analysis = item["analysis"]

    offers.append({
        "Titre": str(offer.get("title") or ""),
        "Entreprise": str(offer.get("company") or ""),
        "Lieu": str(offer.get("location") or ""),
        "Résumé IA": analysis.get("summary") if isinstance(analysis, dict) else analysis,
        "Score IA": analysis.get("score") if isinstance(analysis, dict) else None,
        "URL": offer.get("url")
    })

df = pd.DataFrame(offers)


# ---------------------------------------------------------
# Filtres
# ---------------------------------------------------------
st.sidebar.header("Filtres")

lieux_options = sorted(df["Lieu"].dropna().unique().tolist())
entreprises_options = sorted(df["Entreprise"].dropna().unique().tolist())

lieux = st.sidebar.multiselect("Filtrer par lieu :", lieux_options)
entreprises = st.sidebar.multiselect("Filtrer par entreprise :", entreprises_options)

filtered_df = df.copy()

if lieux:
    filtered_df = filtered_df[filtered_df["Lieu"].isin(lieux)]

if entreprises:
    filtered_df = filtered_df[filtered_df["Entreprise"].isin(entreprises)]

st.sidebar.write(f"📌 Offres après filtre : {len(filtered_df)}")


# ---------------------------------------------------------
# Tableau principal
# ---------------------------------------------------------
st.subheader("📄 Liste des offres analysées")
st.dataframe(filtered_df, width="stretch")


# ---------------------------------------------------------
# Détails d'une offre
# ---------------------------------------------------------
st.subheader("🔍 Détails d'une offre")

if not filtered_df.empty:
    selected_title = st.selectbox(
        "Choisir une offre :",
        filtered_df["Titre"].tolist()
    )

    selected_offer = filtered_df[filtered_df["Titre"] == selected_title].iloc[0]

    st.write(f"### {selected_offer['Titre']}")
    st.write(f"**Entreprise :** {selected_offer['Entreprise']}")
    st.write(f"**Lieu :** {selected_offer['Lieu']}")
    st.write(f"**Résumé IA :** {selected_offer['Résumé IA']}")
    st.write(f"[🔗 Voir l'offre complète]({selected_offer['URL']})")

else:
    st.info("Aucune offre ne correspond aux filtres sélectionnés.")
