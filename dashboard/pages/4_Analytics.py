import streamlit as st
import pandas as pd
from services.api import get_applications

st.title("📊 Analytics")

data = get_applications()
apps = data.get("applications", [])

if not apps:
    st.warning("Pas de données")
    st.stop()

df = pd.DataFrame(apps)

# KPI
col1, col2, col3 = st.columns(3)

col1.metric("Total", len(df))
col2.metric("Score moyen", round(df["score"].mean(), 1))
col3.metric("APPLY", len(df[df["decision"] == "APPLY"]))

st.divider()

# Graph
st.subheader("Scores")
st.bar_chart(df["score"])

st.subheader("Décisions")
st.bar_chart(df["decision"].value_counts())