"""
=====================================================================
📜 PAGE HISTORIQUE - SUIVI DES CANDIDATURES
=====================================================================

🎯 RÔLE :
Cette page affiche l'historique de toutes les candidatures générées
par l'agent. On peut filtrer par statut, par score, etc.

📚 POUR UN DÉBUTANT STREAMLIT :
- st.dataframe() : affiche un tableau interactif
- st.multiselect() : permet de sélectionner plusieurs options
- st.slider() : curseur pour filtrer sur une plage de valeurs
- st.cache_data : met en cache les données pour éviter des appels répétés

=====================================================================
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_BASE_URL = "http://localhost:8000"


@st.cache_data(ttl=30)
def get_applications():
    """
    Récupère la liste des candidatures depuis l'API.
    La mise en cache évite de surcharger le serveur à chaque rafraîchissement.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/agent/applications", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("applications", [])
        else:
            return []
    except Exception as e:
        st.error(f"❌ Erreur de connexion : {e}")
        return []


def show():
    st.title("📜 Historique des candidatures")
    st.markdown("Retrouve toutes les candidatures générées par l'agent.")

    # Récupération des données
    applications = get_applications()

    if not applications:
        st.info("📭 Aucune candidature générée pour le moment.")
        st.markdown("""
        **Comment générer des candidatures ?**
        1. Va dans l'onglet **Lancer l'agent**
        2. Sélectionne ton CV
        3. Lance la recherche
        4. L'agent générera automatiquement des candidatures pour les offres pertinentes
        """)
        return

    # Convertir en DataFrame pandas pour faciliter le filtrage
    df = pd.DataFrame(applications)

    # ==========================================================
    # 📊 STATISTIQUES RAPIDES
    # ==========================================================
    st.markdown("## 📊 Vue d'ensemble")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📝 Total candidatures", len(df))

    with col2:
        if "score" in df.columns:
            avg_score = df["score"].mean()
            st.metric("📊 Score moyen", f"{avg_score:.1f}%")

    with col3:
        if "status" in df.columns:
            status_counts = df["status"].value_counts()
            # Afficher les principaux statuts
            st.markdown("**Répartition par statut**")
            for status, count in status_counts.items():
                st.markdown(f"- {status}: {count}")

    # ==========================================================
    # 🔍 FILTRES
    # ==========================================================
    st.markdown("## 🔍 Filtres")

    col_filter1, col_filter2 = st.columns(2)

    # Filtre par statut (multiselect)
    if "status" in df.columns:
        with col_filter1:
            status_options = df["status"].unique().tolist()
            selected_statuses = st.multiselect(
                "Statut de la candidature",
                options=status_options,
                default=status_options
            )
            if selected_statuses:
                df = df[df["status"].isin(selected_statuses)]

    # Filtre par score (slider)
    if "score" in df.columns:
        with col_filter2:
            min_score = st.slider(
                "Score minimum (%)",
                min_value=0,
                max_value=100,
                value=0,
                step=5
            )
            df = df[df["score"] >= min_score]

    # ==========================================================
    # 📋 TABLEAU DES CANDIDATURES
    # ==========================================================
    st.markdown("## 📋 Liste des candidatures")

    if df.empty:
        st.info("Aucune candidature correspondant aux filtres.")
        return

    # Afficher un tableau interactif
    display_cols = ["title", "company", "location", "score", "status", "created_at"]
    # Garder seulement les colonnes existantes
    available_cols = [col for col in display_cols if col in df.columns]
    st.dataframe(
        df[available_cols],
        use_container_width=True,
        column_config={
            "score": st.column_config.ProgressColumn("Score", format="%d%%", min_value=0, max_value=100),
            "created_at": st.column_config.DatetimeColumn("Date", format="DD/MM/YYYY HH:mm")
        }
    )

    # ==========================================================
    # 🔎 DÉTAIL DE CHAQUE CANDIDATURE (expandable)
    # ==========================================================
    st.markdown("## 🔎 Détail des candidatures")

    for idx, row in df.iterrows():
        with st.expander(f"**{row.get('title', 'Sans titre')}** - {row.get('company', '')} - Score: {row.get('score', 0)}%"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**🏢 Entreprise:** {row.get('company', 'Non spécifiée')}")
                st.markdown(f"**📍 Localisation:** {row.get('location', 'Non spécifiée')}")
                st.markdown(f"**📊 Score:** {row.get('score', 0)}%")
                st.progress(row.get('score', 0) / 100)

            with col2:
                st.markdown(f"**📋 Statut:** {row.get('status', 'inconnu')}")
                created = row.get("created_at", "")
                if created:
                    try:
                        date = datetime.fromisoformat(created)
                        st.markdown(f"**📅 Date:** {date.strftime('%d/%m/%Y %H:%M')}")
                    except:
                        st.markdown(f"**📅 Date:** {created}")

            # Lettre de motivation si disponible
            cover = row.get("cover_letter")
            if cover:
                with st.expander("✉️ Voir la lettre de motivation"):
                    st.write(cover)