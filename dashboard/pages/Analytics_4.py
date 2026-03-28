"""
=====================================================================
📊 PAGE ANALYTICS - STATISTIQUES ET GRAPHIQUES
=====================================================================

🎯 RÔLE :
Affiche des graphiques et statistiques sur les candidatures,
les scores, les secteurs, etc. Utile pour analyser ses performances.

📚 POUR UN DÉBUTANT STREAMLIT :
- st.plotly_chart() : affiche des graphiques interactifs avec Plotly
- st.altair_chart() : alternative avec Altair
- st.metric() : affiche des indicateurs simples
- st.columns() : pour organiser le contenu

=====================================================================
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_BASE_URL = "http://localhost:8000"


@st.cache_data(ttl=30)
def get_applications():
    """Récupère la liste des candidatures"""
    try:
        response = requests.get(f"{API_BASE_URL}/agent/applications", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("applications", [])
        return []
    except Exception as e:
        st.error(f"❌ Erreur de connexion : {e}")
        return []


def show():
    st.title("📊 Analytics")
    st.markdown("Analyse tes candidatures et optimise ta recherche.")

    applications = get_applications()

    if not applications:
        st.info("📭 Aucune donnée disponible. Lance d'abord l'agent pour générer des candidatures.")
        return

    # Convertir en DataFrame
    df = pd.DataFrame(applications)

    # ==========================================================
    # 📈 KPI PRINCIPAUX
    # ==========================================================
    st.markdown("## 📈 Indicateurs clés")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📝 Total candidatures", len(df))

    with col2:
        if "score" in df.columns:
            avg_score = df["score"].mean()
            st.metric("📊 Score moyen", f"{avg_score:.1f}%")

    with col3:
        if "score" in df.columns:
            max_score = df["score"].max()
            st.metric("🏆 Meilleur score", f"{max_score:.0f}%")

    with col4:
        if "created_at" in df.columns:
            # Convertir en datetime et compter les candidatures des 7 derniers jours
            df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
            last_7_days = df[df["created_at"] >= (pd.Timestamp.now() - pd.Timedelta(days=7))]
            st.metric("📅 7 derniers jours", len(last_7_days))

    # ==========================================================
    # 📊 RÉPARTITION PAR STATUT
    # ==========================================================
    if "status" in df.columns:
        st.markdown("## 📊 Répartition par statut")

        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Statut", "Nombre"]

        fig = px.pie(status_counts, values="Nombre", names="Statut", title="Candidatures par statut")
        st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # 📈 ÉVOLUTION DES SCORES DANS LE TEMPS
    # ==========================================================
    if "score" in df.columns and "created_at" in df.columns:
        st.markdown("## 📈 Évolution des scores")

        # Trier par date
        df_sorted = df.sort_values("created_at").copy()
        df_sorted["created_at"] = pd.to_datetime(df_sorted["created_at"])
        df_sorted = df_sorted.dropna(subset=["created_at", "score"])

        if not df_sorted.empty:
            fig = px.line(
                df_sorted,
                x="created_at",
                y="score",
                title="Score de matching au fil du temps",
                labels={"created_at": "Date", "score": "Score (%)"}
            )
            fig.update_layout(xaxis_title="Date", yaxis_title="Score")
            st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # 🏢 TOP ENTREPRISES (si données disponibles)
    # ==========================================================
    if "company" in df.columns:
        st.markdown("## 🏢 Top entreprises ciblées")

        company_counts = df["company"].value_counts().head(10).reset_index()
        company_counts.columns = ["Entreprise", "Nombre"]

        fig = px.bar(
            company_counts,
            x="Entreprise",
            y="Nombre",
            title="Entreprises les plus postulées",
            color="Nombre"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # 📊 BOXPLOT DES SCORES PAR STATUT
    # ==========================================================
    if "score" in df.columns and "status" in df.columns:
        st.markdown("## 📊 Distribution des scores par statut")

        fig = px.box(
            df,
            x="status",
            y="score",
            title="Distribution des scores selon le statut",
            labels={"status": "Statut", "score": "Score (%)"}
        )
        st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # 🔍 RECOMMANDATIONS (insights)
    # ==========================================================
    st.markdown("## 💡 Recommandations")

    # Calcul du score moyen
    avg_score = df["score"].mean() if "score" in df.columns else 0

    # Taux de candidatures "acceptées" (si ce statut existe)
    if "status" in df.columns:
        accepted = df[df["status"] == "accepted"].shape[0]
        total = df.shape[0]
        if total > 0:
            accept_rate = (accepted / total) * 100
        else:
            accept_rate = 0
    else:
        accept_rate = 0

    col_rec1, col_rec2 = st.columns(2)

    with col_rec1:
        if avg_score < 50:
            st.warning("📉 Ton score de matching moyen est inférieur à 50%. Essaye d'ajuster ton CV pour mieux cibler les offres.")
        else:
            st.success("✅ Ton score de matching est bon ! Continue comme ça.")

    with col_rec2:
        if accept_rate < 20:
            st.info("📉 Ton taux d'acceptation est faible. Peut-être peux-tu améliorer la personnalisation de tes lettres.")
        else:
            st.success("✅ Bon taux d'acceptation !")

    st.markdown("---")
    st.caption("Ces analyses sont basées sur les données des candidatures générées.")