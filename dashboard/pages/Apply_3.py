"""
=====================================================================
✍️ PAGE POSTULER - GÉNÉRATION DE CANDIDATURE COMPLÈTE
=====================================================================
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime
from typing import List, Optional

API_BASE_URL = "http://localhost:8000"


# ==============================================================
# FONCTIONS
# ==============================================================

def get_cv_list():
    """Récupère la liste des CV disponibles."""
    try:
        response = requests.get(f"{API_BASE_URL}/agent/cv/list", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("cvs", []), data.get("last_cv")
        return [], None
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return [], None


def generate_letter(job, cv_name):
    """Génère une lettre de motivation."""
    try:
        job_data = {
            "title": job.get("title", ""),
            "description": job.get("description", ""),
            "location": job.get("location", ""),
            "company": job.get("company", ""),
            "url": job.get("url", ""),
            "match_score": job.get("match_score", 0),
            "should_apply": job.get("should_apply", False),
            "missing_skills": job.get("missing_skills", []),
            "strengths": job.get("strengths", [])
        }
        
        payload = {
            "job": job_data,
            "cv_name": cv_name,
            "match_threshold": 0
        }
        
        response = requests.post(
            f"{API_BASE_URL}/agent/apply",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Erreur: {e}")
        return None


def optimize_cv_frontend(cv_name, job_title, job_description, missing_skills, strengths):
    """Optimise le CV pour l'offre."""
    try:
        payload = {
            "cv_name": cv_name,
            "job_title": job_title,
            "job_description": job_description,
            "missing_skills": missing_skills,
            "strengths": strengths
        }
        
        response = requests.post(
            f"{API_BASE_URL}/cv/optimize",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": response.text}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================
# PAGE PRINCIPALE
# ==============================================================

def show():
    """Affiche la page de candidature."""
    st.title("✍️ Postuler à une offre")
    st.markdown("Génère une lettre de motivation et un CV optimisé pour l'offre sélectionnée.")
    
    # ==========================================================
    # RÉCUPÉRATION DE L'OFFRE
    # ==========================================================
    selected_job = st.session_state.get("selected_offer") or st.session_state.get("selected_job")
    
    if not selected_job:
        st.warning("⚠️ Aucune offre sélectionnée.")
        st.markdown("""
        **Pour postuler à une offre :**
        1. Va dans la page **Lancer l'agent**
        2. Lance une recherche d'offres
        3. Clique sur **Postuler** pour une offre qui t'intéresse
        """)
        
        if st.button("← Retour à la recherche", use_container_width=True):
            st.session_state["page"] = "🎯 Lancer l'agent"
            st.rerun()
        return
    
    # ==========================================================
    # AFFICHAGE DE L'OFFRE
    # ==========================================================
    st.success(f"✅ Offre sélectionnée : **{selected_job.get('title', 'Titre non spécifié')}**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🏢 Entreprise :** {selected_job.get('company', 'Non spécifiée')}")
        st.markdown(f"**📍 Localisation :** {selected_job.get('location', 'Non spécifiée')}")
    with col2:
        match_score = selected_job.get("match_score", selected_job.get("score", 0))
        st.markdown(f"**📊 Score :** {match_score}%")
        st.progress(match_score / 100)
    
    # Afficher les compétences
    missing_skills = selected_job.get("missing_skills", [])
    strengths = selected_job.get("strengths", [])
    
    if missing_skills or strengths:
        col1, col2 = st.columns(2)
        with col1:
            if strengths:
                st.markdown("**✅ Points forts :**")
                for s in strengths[:5]:
                    st.markdown(f"- {s}")
        with col2:
            if missing_skills:
                st.markdown("**⚠️ Compétences à valoriser :**")
                for s in missing_skills[:5]:
                    st.markdown(f"- {s}")
    
    st.divider()
    
    # ==========================================================
    # SÉLECTION DU CV
    # ==========================================================
    st.markdown("## 📄 CV à utiliser")
    
    cv_list, last_cv = get_cv_list()
    if cv_list and isinstance(cv_list[0], dict):
        cv_names = [cv.get("filename") for cv in cv_list if cv.get("filename")]
    else:
        cv_names = cv_list
    
    if not cv_names:
        st.warning("⚠️ Aucun CV disponible.")
        if st.button("📤 Uploader un CV", use_container_width=True):
            st.session_state["page"] = "🎯 Lancer l'agent"
            st.rerun()
        return
    
    default_idx = cv_names.index(last_cv) if last_cv in cv_names else 0
    selected_cv = st.selectbox("Choisis ton CV", cv_names, index=default_idx)
    
    # ==========================================================
    # ONGLETS POUR LES DIFFÉRENTES PARTIES
    # ==========================================================
    tab1, tab2, tab3 = st.tabs(["📝 Lettre de motivation", "📄 CV optimisé", "📦 Pack complet"])
    
    # ==========================================================
    # TAB 1 : LETTRE DE MOTIVATION
    # ==========================================================
    with tab1:
        st.markdown("### ✉️ Lettre de motivation")
        
        if st.button("🎨 GÉNÉRER LA LETTRE", type="primary", use_container_width=True):
            with st.spinner("Génération de la lettre en cours..."):
                result = generate_letter(selected_job, selected_cv)
            
            if result:
                st.session_state["generated_letter"] = result.get("cover_letter", "")
                st.session_state["generated_success"] = True
                st.success("✅ Lettre générée avec succès !")
                st.rerun()
        
        if st.session_state.get("generated_success"):
            letter = st.session_state.get("generated_letter", "")
            
            edited = st.text_area(
                "Modifie ta lettre si besoin",
                value=letter,
                height=400
            )
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Télécharger (TXT)",
                    data=edited,
                    file_name=f"lettre_motivation_{selected_job.get('title', '').replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                # Génération PDF de la lettre
                if st.button("📄 Télécharger (PDF)", use_container_width=True):
                    with st.spinner("Génération du PDF..."):
                        pdf_result = requests.post(
                            f"{API_BASE_URL}/pdf/letter",
                            json={
                                "text": edited,
                                "job_title": selected_job.get("title", ""),
                                "company": selected_job.get("company", "")
                            }
                        )
                        if pdf_result.status_code == 200:
                            pdf_data = pdf_result.json()
                            with open(pdf_data.get("path", ""), "rb") as f:
                                st.download_button(
                                    label="📥 Télécharger le PDF",
                                    data=f,
                                    file_name=pdf_data.get("filename", "lettre.pdf"),
                                    mime="application/pdf"
                                )
    
    # ==========================================================
    # TAB 2 : CV OPTIMISÉ
    # ==========================================================
    with tab2:
        st.markdown("### 📄 CV optimisé pour l'offre")
        st.info("Le CV sera adapté pour mettre en avant les compétences recherchées par l'entreprise.")
        
        if st.button("🎯 GÉNÉRER LE CV OPTIMISÉ", type="secondary", use_container_width=True):
            with st.spinner("Optimisation du CV en cours..."):
                result = optimize_cv_frontend(
                    cv_name=selected_cv,
                    job_title=selected_job.get("title", ""),
                    job_description=selected_job.get("description", ""),
                    missing_skills=missing_skills,
                    strengths=strengths
                )
            
            if result and result.get("success"):
                st.session_state["optimized_cv"] = result.get("optimized_text", "")
                st.session_state["optimized_cv_path"] = result.get("pdf_path", "")
                st.success("✅ CV optimisé généré avec succès !")
                st.rerun()
            else:
                st.error(f"❌ Erreur : {result.get('error', 'Inconnue')}")
        
        if st.session_state.get("optimized_cv"):
            with st.expander("📄 Aperçu du CV optimisé", expanded=True):
                st.markdown(st.session_state["optimized_cv"])
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Télécharger (TXT)",
                    data=st.session_state["optimized_cv"],
                    file_name=f"CV_optimise_{selected_job.get('title', '').replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                if st.session_state.get("optimized_cv_path"):
                    with open(st.session_state["optimized_cv_path"], "rb") as f:
                        st.download_button(
                            label="📄 Télécharger (PDF)",
                            data=f,
                            file_name=os.path.basename(st.session_state["optimized_cv_path"]),
                            mime="application/pdf",
                            use_container_width=True
                        )
    
    # ==========================================================
    # TAB 3 : PACK COMPLET
    # ==========================================================
    with tab3:
        st.markdown("### 📦 Pack de candidature complet")
        st.markdown("Génère la lettre et le CV optimisé en un seul clic.")
        
        if st.button("🚀 GÉNÉRER LE PACK COMPLET", type="primary", use_container_width=True):
            with st.spinner("Génération du pack en cours..."):
                # Générer la lettre
                letter_result = generate_letter(selected_job, selected_cv)
                
                # Générer le CV optimisé
                cv_result = optimize_cv_frontend(
                    cv_name=selected_cv,
                    job_title=selected_job.get("title", ""),
                    job_description=selected_job.get("description", ""),
                    missing_skills=missing_skills,
                    strengths=strengths
                )
                
                if letter_result and cv_result and cv_result.get("success"):
                    st.session_state["generated_letter"] = letter_result.get("cover_letter", "")
                    st.session_state["optimized_cv"] = cv_result.get("optimized_text", "")
                    st.session_state["optimized_cv_path"] = cv_result.get("pdf_path", "")
                    st.session_state["pack_generated"] = True
                    st.success("✅ Pack complet généré avec succès !")
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la génération du pack")
        
        if st.session_state.get("pack_generated"):
            st.markdown("---")
            st.markdown("### 📄 Documents prêts à être téléchargés")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Lettre de motivation**")
                st.download_button(
                    label="📥 Télécharger la lettre",
                    data=st.session_state.get("generated_letter", ""),
                    file_name=f"lettre_{selected_job.get('title', '').replace(' ', '_')}.txt",
                    use_container_width=True
                )
            
            with col2:
                st.markdown("**CV optimisé**")
                st.download_button(
                    label="📥 Télécharger le CV",
                    data=st.session_state.get("optimized_cv", ""),
                    file_name=f"CV_{selected_job.get('title', '').replace(' ', '_')}.txt",
                    use_container_width=True
                )
            
            st.success("💡 Astuce : Tu peux maintenant envoyer ces documents à l'entreprise !")
    
    # ==========================================================
    # BOUTON RETOUR
    # ==========================================================
    st.divider()
    if st.button("← Retour aux offres", use_container_width=True):
        st.session_state["page"] = "🎯 Lancer l'agent"
        st.rerun()


if __name__ == "__main__":
    show()