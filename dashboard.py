import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# =========================================================
# CONFIG
# =========================================================
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Agent IA Emploi",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Agent IA de Recherche d'Emploi")
st.markdown("Assistant intelligent pour sélectionner et préparer tes candidatures")

# =========================================================
# LOAD JOBS
# =========================================================
@st.cache_data(ttl=60)
def load_jobs():
    try:
        r = requests.get(f"{API_URL}/jobs", timeout=5)
        if r.status_code == 200:
            return r.json().get("data", [])
    except:
        return []
    return []

data = load_jobs()

if not data:
    st.warning("⚠️ Aucune offre disponible")
    st.stop()

# =========================================================
# TRANSFORMATION DATA
# =========================================================
rows = []

for i, item in enumerate(data):

    offer = item.get("offer", {})
    analysis = item.get("analysis", {})

    rows.append({
        "id": i,
        "Titre": offer.get("title", ""),
        "Entreprise": offer.get("company", ""),
        "Lieu": offer.get("location", ""),
        "Score": float(analysis.get("matching_score", 0)),
        "URL": offer.get("url", ""),
        "Résumé": analysis.get("resume", ""),
        "Skills": " ".join(analysis.get("hard_skills", []))
    })

df = pd.DataFrame(rows)

# =========================================================
# SIDEBAR (CV + paramètres)
# =========================================================
with st.sidebar:
    st.header("📄 Ton profil")

    cv_text = st.text_area(
        "Ton CV",
        height=150,
        value=st.session_state.get(
            "cv_text",
            "Python, SQL, data analyse, travail en équipe"
        )
    )

    st.session_state["cv_text"] = cv_text

    st.markdown("---")
    st.header("⚙️ Paramètres IA")

    min_score = st.slider("Score minimum", 0, 100, 70)
    max_apply = st.slider("Nombre max d'offres", 1, 10, 5)

# =========================================================
# MATCHING INTELLIGENT
# =========================================================
def compute_score(row, cv):
    score = row["Score"]
    bonus = 0

    cv = cv.lower()

    if "python" in cv and "python" in row["Skills"].lower():
        bonus += 5

    if "data" in cv and "data" in row["Résumé"].lower():
        bonus += 5

    return score + bonus

df["Score_Final"] = df.apply(lambda x: compute_score(x, cv_text), axis=1)

# =========================================================
# KPI
# =========================================================
col1, col2, col3 = st.columns(3)

col1.metric("📦 Offres", len(df))
col2.metric("⭐ Score moyen", round(df["Score_Final"].mean(), 1))
col3.metric("🔥 Meilleur score", df["Score_Final"].max())

# =========================================================
# GRAPH
# =========================================================
fig = px.histogram(df, x="Score_Final", nbins=10)
st.plotly_chart(fig, use_container_width=True)

# =========================================================
# TOP JOBS (sélection IA)
# =========================================================
top_jobs = (
    df
    .sort_values(by="Score_Final", ascending=False)
    .query("Score_Final >= @min_score")
    .head(max_apply)
)

st.markdown("---")
st.header("🎯 Offres recommandées")

st.dataframe(top_jobs, use_container_width=True)

# =========================================================
# SÉLECTION OFFRE (SAFE)
# =========================================================
selected_job = None

if not top_jobs.empty:

    selected_id = st.selectbox(
        "Choisir une offre",
        top_jobs["id"]
    )

    selected_job = top_jobs[top_jobs["id"] == selected_id].iloc[0]

    st.markdown(f"### {selected_job['Titre']}")
    st.write(f"🏢 {selected_job['Entreprise']}")
    st.write(f"📍 {selected_job['Lieu']}")
    st.write(f"⭐ Score : {selected_job['Score_Final']}")

    if selected_job["URL"]:
        st.markdown(f"[🔗 Voir l'offre]({selected_job['URL']})")

# =========================================================
# GÉNÉRATION IA
# =========================================================
if st.button("🧠 Générer CV + Lettre"):

    if selected_job is None:
        st.warning("⚠️ Sélectionne une offre")
        st.stop()

    with st.spinner("Génération IA..."):

        payload = {
            "job": {
                "id": str(selected_job["id"]),  # ✅ FIX CRITIQUE
                "title": selected_job["Titre"],
                "company": selected_job["Entreprise"],
                "description": selected_job["Résumé"]
            },
            "cv_text": cv_text
        }

        try:
            r = requests.post(
                f"{API_URL}/applications/build",
                json=payload,
                timeout=20
            )

            if r.status_code == 200:
                result = r.json()

                st.session_state["generated_cv"] = result.get("cv", "")
                st.session_state["generated_letter"] = result.get("cover_letter", "")

                st.success("✅ Généré avec succès")

            else:
                st.error(f"❌ Backend {r.status_code}")
                st.write(r.text)

        except Exception as e:
            st.error(f"Erreur : {e}")

# =========================================================
# AFFICHAGE + ÉDITION
# =========================================================
if "generated_cv" in st.session_state:

    st.subheader("📄 CV personnalisé")

    st.session_state["generated_cv"] = st.text_area(
        "Modifier ton CV",
        st.session_state["generated_cv"],
        height=300
    )

if "generated_letter" in st.session_state:

    st.subheader("✉️ Lettre de motivation")

    st.session_state["generated_letter"] = st.text_area(
        "Modifier ta lettre",
        st.session_state["generated_letter"],
        height=300
    )

# =========================================================
# POSTULER (MANUEL)
# =========================================================
if st.button("🚀 Postuler avec ces documents"):

    if selected_job is None:
        st.warning("⚠️ Sélectionne une offre")
        st.stop()

    if "generated_cv" not in st.session_state:
        st.warning("⚠️ Génère d'abord un CV")
        st.stop()

    payload = {
        "job": {
            "id": str(selected_job["id"]),
            "title": selected_job["Titre"],
            "company": selected_job["Entreprise"]
        },
        "cv": st.session_state.get("generated_cv", ""),
        "cover_letter": st.session_state.get("generated_letter", "")
    }

    try:
        r = requests.post(
            f"{API_URL}/applications/submit",
            json=payload
        )

        if r.status_code == 200:
            st.success("✅ Candidature envoyée")
        else:
            st.error(f"❌ Échec {r.status_code}")

    except Exception as e:
        st.error(f"Erreur : {e}")
        
# =========================================================
# 🤖 AGENT AUTONOME
# =========================================================
st.markdown("---")
st.header("🤖 Agent Autonome")

st.write("L'agent analyse toutes les offres et génère automatiquement les meilleures candidatures.")

if st.button("🚀 Lancer l'agent IA"):

    with st.spinner("Agent en cours d'exécution..."):

        payload = {
            "jobs": data,
            "cv_text": cv_text,
            "min_score": min_score
        }

        try:
            r = requests.post(
                f"{API_URL}/agent/run",
                json=payload,
                timeout=120
            )

            if r.status_code == 200:
                results = r.json().get("results", [])
                st.session_state["agent_results"] = results
                st.success("✅ Agent terminé")

            else:
                st.error(f"❌ Erreur backend {r.status_code}")
                st.write(r.text)

        except Exception as e:
            st.error(f"Erreur : {e}")
            
if "agent_results" in st.session_state:
    st.info("💡 Mode autonome : l'IA travaille pour toi")
    st.header("🎯 Résultats de l'agent")

    results = st.session_state["agent_results"]

    if not results:
        st.info("Aucune offre pertinente trouvée")
    else:
        for res in results:

            job = res["job"]
            app_data = res["application"]

            st.markdown(f"### {job['title']} - {job['company']}")
            st.write(f"⭐ Score : {res['score']}")

            with st.expander("📄 CV généré"):
                st.write(app_data.get("cv", ""))

            with st.expander("✉️ Lettre générée"):
                st.write(app_data.get("cover_letter", ""))

            st.markdown("---")