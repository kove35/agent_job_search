"""
=====================================================================
📦 APPLICATION BUILDER - GÉNÉRATION DE CANDIDATURE
=====================================================================

🎯 RÔLE DE CE FICHIER :
Ce fichier construit le pack de candidature complet :
- Lettre de motivation personnalisée
- CV optimisé pour l'offre
- Analyse du CV vs l'offre
- Score de matching

📚 POUR UN DÉBUTANT :
Ce fichier assemble toutes les pièces pour créer une candidature.
Il utilise :
- Le texte du CV extrait
- Les coordonnées depuis user_config (fichier de configuration)
- L'analyse de l'offre par l'IA
- Pour générer une lettre personnalisée et un CV optimisé

=====================================================================
"""

from typing import Optional, Dict, Any
from datetime import datetime
import os

from app.models.job_offer import JobOffer
from app.services.cv_optimizer import optimize_cv_for_job
from app.services.pdf_generator import generate_pdf as text_to_pdf

# ==============================================================
# 📦 IMPORT DES SERVICES
# ==============================================================
from app.services.cv_extraction import extract_text_from_pdf
from app.services.ai_agent import analyze_offer_with_cv

# ✅ IMPORTER LA CONFIG UTILISATEUR (au lieu d'extraire les coordonnées du CV)
from app.core.user_config import USER_CONFIG


# ==============================================================
# 🔧 FONCTION POUR RÉCUPÉRER LES COORDONNÉES
# ==============================================================

def get_contact_info() -> Dict[str, str]:
    """
    Récupère les coordonnées de l'utilisateur depuis user_config.py.
    
    ✅ Avantages :
    - Coordonnées propres et contrôlées
    - Pas de risque d'erreur d'extraction
    - Formatage correct (pas de majuscules forcées)
    
    Returns:
        Dictionnaire avec les coordonnées
    """
    return {
        "name": USER_CONFIG.get("name", ""),
        "address": USER_CONFIG.get("address", ""),
        "email": USER_CONFIG.get("email", ""),
        "phone": USER_CONFIG.get("phone", "")
    }


# ==============================================================
# 🔧 CLASSE PACK DE CANDIDATURE
# ==============================================================

class ApplicationPack:
    """
    Classe qui contient toutes les informations d'une candidature.
    
    📚 EXPLICATION :
    Une classe est comme un moule qui définit la structure d'un objet.
    Chaque candidature a un job, une lettre, un score, etc.
    """
    
    def __init__(self, job, cv_text, cover_letter, match_score, missing_skills, strengths, 
                 optimized_cv_text=None, optimized_cv_path=None, user_id=None):
        """
        Constructeur : initialise un nouvel objet ApplicationPack.
        
        Args:
            job (JobOffer): L'offre d'emploi
            cv_text (str): Le texte du CV original
            cover_letter (str): La lettre de motivation générée
            match_score (float): Score de compatibilité (0-100)
            missing_skills (list): Compétences manquantes
            strengths (list): Points forts du candidat
            optimized_cv_text (str, optional): Texte du CV optimisé
            optimized_cv_path (str, optional): Chemin du PDF du CV optimisé
            user_id (int, optional): ID de l'utilisateur
        """
        self.job = job
        self.cv_text = cv_text
        self.cover_letter = cover_letter
        self.match_score = match_score
        self.missing_skills = missing_skills
        self.strengths = strengths
        self.optimized_cv_text = optimized_cv_text
        self.optimized_cv_path = optimized_cv_path
        self.user_id = user_id
        self.created_at = datetime.now()


# ==============================================================
# 🔧 FONCTION PRINCIPALE : CONSTRUIRE LE PACK DE CANDIDATURE
# ==============================================================

def build_application_pack(
    job: JobOffer,
    cv_pdf_path: str,
    user_id: Optional[int] = None,
    save_to_db: bool = True,
    generate_pdf: bool = False,
    optimize_cv: bool = True
) -> ApplicationPack:
    """
    Génère un pack de candidature complet (lettre + analyse + CV optimisé).
    
    📚 EXPLICATION POUR DÉBUTANT :
    Cette fonction est le cœur de la génération de candidature.
    Elle fait plusieurs choses dans l'ordre :
    1. Extraire le texte du CV
    2. Récupérer les coordonnées depuis user_config (plus d'extraction hasardeuse)
    3. Analyser l'offre par rapport au CV
    4. Générer une lettre de motivation personnalisée
    5. Optimiser le CV pour l'offre (optionnel)
    6. Sauvegarder le tout
    
    Args:
        job (JobOffer): L'offre d'emploi
        cv_pdf_path (str): Chemin vers le fichier PDF du CV
        user_id (int, optional): ID de l'utilisateur
        save_to_db (bool): Sauvegarder en base de données ?
        generate_pdf (bool): Générer un PDF de la lettre ?
        optimize_cv (bool): Générer une version optimisée du CV ?
    
    Returns:
        ApplicationPack: L'objet contenant toutes les informations
    
    Raises:
        ValueError: Si l'extraction du CV échoue
    """
    
    print("=" * 50)
    print("📝 DÉBUT DE LA GÉNÉRATION DE CANDIDATURE")
    print("=" * 50)
    
    # ==========================================================
    # ÉTAPE 1 : Extraire le texte du CV
    # ==========================================================
    print("📄 Étape 1/6 : Extraction du texte du CV...")
    texte_cv = extract_text_from_pdf(cv_pdf_path)
    
    if not texte_cv:
        erreur = "Impossible d'extraire le texte du CV. Vérifie que le fichier est un PDF texte (pas une image scannée)."
        print(f"❌ Erreur : {erreur}")
        raise ValueError(erreur)
    
    print(f"✅ Texte extrait : {len(texte_cv)} caractères")
    
    # ==========================================================
    # ÉTAPE 2 : Récupérer les coordonnées depuis user_config
    # ==========================================================
    print("📇 Étape 2/6 : Récupération des coordonnées depuis user_config...")
    contact_info = get_contact_info()
    
    print(f"   📛 Nom : {contact_info['name']}")
    print(f"   📧 Email : {contact_info['email']}")
    print(f"   📞 Téléphone : {contact_info['phone']}")
    print(f"   📍 Adresse : {contact_info['address'][:50]}..." if len(contact_info['address']) > 50 else f"   📍 Adresse : {contact_info['address']}")
    
    # ==========================================================
    # ÉTAPE 3 : Analyser l'offre par rapport au CV
    # ==========================================================
    print("🤖 Étape 3/6 : Analyse de l'offre par l'IA...")
    analyse = analyze_offer_with_cv(texte_cv, job)
    
    score = analyse.get("match_score", 0)
    competences_manquantes = analyse.get("missing_skills", [])
    points_forts = analyse.get("strengths", [])
    
    print(f"   📊 Score de matching : {score}%")
    print(f"   ✅ Points forts : {len(points_forts)} trouvés")
    print(f"   ❌ Compétences manquantes : {len(competences_manquantes)} trouvées")
    
    # ==========================================================
    # ÉTAPE 4 : Générer la lettre de motivation
    # ==========================================================
    print("✍️ Étape 4/6 : Génération de la lettre de motivation...")
    
    date_aujourdhui = datetime.now().strftime("%d/%m/%Y")
    
    # Récupérer les coordonnées nettoyées
    nom_complet = contact_info.get("name", "[Prénom Nom]")
    adresse = contact_info.get("address", "")
    telephone = contact_info.get("phone", "")
    email = contact_info.get("email", "")
    
    # Construction de la lettre ligne par ligne
    lettre = ""
    
    # Bloc d'en-tête (coordonnées)
    lettre += f"{nom_complet}\n"
    if adresse:
        # Nettoyer l'adresse (supprimer les retours à la ligne excessifs)
        adresse_propre = adresse.replace('\n\n', '\n').strip()
        lettre += f"{adresse_propre}\n"
    if telephone:
        lettre += f"{telephone}\n"
    if email:
        lettre += f"{email}\n"
    lettre += f"\n{date_aujourdhui}\n\n"
    
    # Informations de l'entreprise
    nom_entreprise = job.company if job.company else "l'entreprise"
    localisation = job.location if job.location else "votre agence"
    titre_poste = job.title if job.title else "le poste proposé"
    
    lettre += f"{nom_entreprise}\n"
    if localisation:
        lettre += f"{localisation}\n"
    lettre += "\n"
    
    # Objet de la lettre
    lettre += f"Objet : Candidature au poste de {titre_poste}\n\n"
    
    # Formule d'appel
    lettre += "Madame, Monsieur,\n\n"
    
    # Introduction
    lettre += f"Je vous écris pour exprimer mon vif intérêt pour le poste de {titre_poste} au sein de {nom_entreprise}.\n\n"
    
    # Paragraphe des compétences (points forts)
    if points_forts:
        lettre += "Mon parcours professionnel m'a permis de développer des compétences solides dans les domaines suivants :\n\n"
        for point_fort in points_forts[:5]:
            lettre += f"- {point_fort}\n"
        lettre += "\n"
    
    # Paragraphe de motivation
    if localisation:
        lettre += f"La perspective de contribuer à l'efficacité de votre équipe à {localisation} m'enthousiasme, "
    else:
        lettre += "La perspective de contribuer à l'efficacité de votre équipe m'enthousiasme, "
    lettre += f"et je suis convaincu que mes compétences techniques et mon engagement seront des atouts précieux pour {nom_entreprise}.\n\n"
    
    # Conclusion
    lettre += "Je vous remercie de l'attention portée à ma candidature et reste à votre disposition pour un entretien.\n\n"
    
    # Formule de politesse
    lettre += "Cordialement,\n\n"
    lettre += f"{nom_complet}\n"
    
    print("✅ Lettre générée avec succès")
    
    # ==========================================================
    # ÉTAPE 5 : Optimiser le CV pour l'offre
    # ==========================================================
    optimized_cv_text = None
    optimized_cv_path = None
    
    if optimize_cv:
        print("📄 Étape 5/6 : Optimisation du CV pour l'offre...")
        try:
            # Récupérer les informations du job
            job_title = job.title if hasattr(job, 'title') else job.get("title", "")
            job_description = job.description if hasattr(job, 'description') else job.get("description", "")
            
            # Générer le CV optimisé
            optimized_cv_text = optimize_cv_for_job(
                cv_text=texte_cv,
                job_title=job_title,
                job_description=job_description,
                missing_skills=competences_manquantes,
                strengths=points_forts
            )
            
            # Sauvegarder le CV optimisé en PDF
            if generate_pdf and optimized_cv_text:
                safe_title = job_title.replace(' ', '_').replace('/', '_')
                output_path = f"storage/optimized_cv/{safe_title}_optimized.pdf"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                optimized_cv_path = text_to_pdf(optimized_cv_text, output_path)
                print(f"✅ CV optimisé généré : {optimized_cv_path}")
            
        except Exception as e:
            print(f"⚠️ Erreur lors de l'optimisation du CV : {e}")
    
    # ==========================================================
    # ÉTAPE 6 : Créer l'objet ApplicationPack
    # ==========================================================
    print("📦 Étape 6/6 : Création du pack de candidature...")
    
    pack = ApplicationPack(
        job=job,
        cv_text=texte_cv,
        cover_letter=lettre,
        match_score=score,
        missing_skills=competences_manquantes,
        strengths=points_forts,
        optimized_cv_text=optimized_cv_text,
        optimized_cv_path=optimized_cv_path,
        user_id=user_id
    )
    
    # ==========================================================
    # SAUVEGARDE OPTIONNELLE EN BASE DE DONNÉES
    # ==========================================================
    if save_to_db:
        try:
            from app.services.storage.application_storage import save_application
            save_application(pack)
            print("💾 Candidature sauvegardée en base de données")
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde : {e}")
    
    print("=" * 50)
    print("✅ CANDIDATURE GÉNÉRÉE AVEC SUCCÈS !")
    print("=" * 50)
    
    return pack