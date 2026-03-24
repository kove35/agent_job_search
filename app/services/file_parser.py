# =========================================================
# 📄 FILE PARSER SERVICE
# =========================================================
# 🎯 RÔLE :
# Extraire le texte brut d’un CV PDF
#
# 👉 C’est le POINT D’ENTRÉE de ton pipeline IA
#
# 🔁 UTILISATION DANS TON APP :
# FastAPI (router) reçoit un fichier → appelle cette fonction
#
# 📍 APPELÉ DANS :
# app/routers/agents.py
#
# 🔥 FLOW :
# Upload CV → extract_text_from_pdf → texte → IA (profil + scoring)
#
# ⚠️ IMPORTANT :
# - Ne fonctionne PAS avec PDF scannés (image)
# - Nécessite OCR si PDF image
#
# =========================================================

import pdfplumber
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extrait le texte d’un fichier PDF

    INPUT :
    - file_bytes : contenu brut du fichier PDF

    OUTPUT :
    - string : texte extrait du CV

    UTILISATION :
    cv_text = extract_text_from_pdf(file_bytes)
    """

    text = ""

    try:
        # Ouverture du PDF depuis la mémoire (sans sauvegarde disque)
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:

            # Parcours des pages
            for page in pdf.pages:
                page_text = page.extract_text()

                # Ajout du texte si présent
                if page_text:
                    text += page_text + "\n"

    except Exception as e:
        print("❌ Erreur extraction PDF:", e)

    # Nettoyage minimal
    text = text.strip()

    return text