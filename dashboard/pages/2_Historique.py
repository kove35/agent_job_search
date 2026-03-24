import streamlit as st
from dashboard.services.api import get_history

st.title("📊 Historique")

history = get_history()

if not history:
    st.info("Aucune donnée")

else:
    for job in history:
        st.write(job)