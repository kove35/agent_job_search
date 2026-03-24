import streamlit as st

def filter_section():
    """
    Crée les filtres dans la sidebar
    """

    st.sidebar.title("🎛️ Filtres")

    # Filtre score minimum
    min_score = st.sidebar.slider(
        "Score minimum",
        0, 100, 50
    )

    # Filtre décision
    decision_filter = st.sidebar.multiselect(
        "Décision",
        ["APPLY", "SKIP"],
        default=["APPLY", "SKIP"]
    )

    # Tri
    sort_order = st.sidebar.selectbox(
        "Tri",
        ["Score décroissant", "Score croissant"]
    )
    # =========================
    # NOUVEAU
    # =========================
    max_jobs = st.slider("🔢 Nombre d'offres", 5, 50, 10)

    location = st.text_input(
    "📍 Zone géographique",
    placeholder="Paris, Lyon, France..."
    )
    return min_score, decision_filter, sort_order,max_jobs,location