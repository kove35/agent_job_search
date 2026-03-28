"""
=====================================================================
📄 PDF GENERATOR - GÉNÉRATION DE DOCUMENTS PDF
=====================================================================

🎯 RÔLE DE CE FICHIER :
Génère des fichiers PDF à partir de texte pour :
- Lettres de motivation
- CV optimisés
- Packs de candidature complets

📚 POUR UN DÉBUTANT :
reportlab est une bibliothèque qui permet de créer des PDF
programmatiquement. On dessine le texte ligne par ligne sur une page.

=====================================================================
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

# ==============================================================
# 📁 CONFIGURATION
# ==============================================================

# Dossier de sortie pour les PDF générés
OUTPUT_FOLDER = "generated_docs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Taille de page
PAGE_SIZE = A4
PAGE_WIDTH, PAGE_HEIGHT = A4

# Marges (en points, 1 pt = 1/72 pouce)
MARGIN_LEFT = 40
MARGIN_RIGHT = 40
MARGIN_TOP = 40
MARGIN_BOTTOM = 40

# Interligne
LINE_HEIGHT = 15


# ==============================================================
# 🔧 FONCTION DE GÉNÉRATION PDF SIMPLE
# ==============================================================

def generate_pdf(text: str, filename_prefix: str = "doc") -> Optional[str]:
    """
    🎯 Génère un PDF simple à partir de texte.
    
    Args:
        text (str): Le texte à convertir en PDF
        filename_prefix (str): Préfixe pour le nom du fichier
    
    Returns:
        str: Chemin du fichier PDF généré, ou None en cas d'erreur
    """
    try:
        # Générer un ID unique pour le fichier
        file_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(OUTPUT_FOLDER, f"{filename_prefix}_{timestamp}_{file_id}.pdf")
        
        # Créer le canvas PDF
        c = canvas.Canvas(file_path, pagesize=PAGE_SIZE)
        c.setFont("Helvetica", 11)
        
        # Position initiale (en haut de la page)
        y = PAGE_HEIGHT - MARGIN_TOP
        
        # Découper le texte en lignes
        lines = text.split("\n")
        
        for line in lines:
            # Si on arrive en bas de page, créer une nouvelle page
            if y < MARGIN_BOTTOM:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = PAGE_HEIGHT - MARGIN_TOP
            
            # Dessiner la ligne
            c.drawString(MARGIN_LEFT, y, line)
            
            # Descendre d'une ligne
            y -= LINE_HEIGHT
        
        # Sauvegarder le PDF
        c.save()
        
        return file_path
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF : {e}")
        return None


# ==============================================================
# 🔧 FONCTION DE GÉNÉRATION PDF AVEC MISE EN PAGE
# ==============================================================

def generate_letter_pdf(
    letter_text: str,
    job_title: str,
    company: str,
    user_name: str
) -> Optional[str]:
    """
    🎯 Génère un PDF formaté pour une lettre de motivation.
    
    Args:
        letter_text: Texte complet de la lettre
        job_title: Titre du poste
        company: Nom de l'entreprise
        user_name: Nom du candidat
    
    Returns:
        str: Chemin du PDF généré
    """
    try:
        # Créer un nom de fichier unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = job_title.replace(' ', '_').replace('/', '_')
        safe_company = company.replace(' ', '_').replace('/', '_')
        filename = f"lettre_motivation_{safe_company}_{safe_title}_{timestamp}.pdf"
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        
        # Créer le canvas
        c = canvas.Canvas(file_path, pagesize=PAGE_SIZE)
        c.setFont("Helvetica", 11)
        
        y = PAGE_HEIGHT - MARGIN_TOP
        lines = letter_text.split("\n")
        
        for line in lines:
            if y < MARGIN_BOTTOM:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = PAGE_HEIGHT - MARGIN_TOP
            
            # Mettre en gras certains éléments
            if "Objet :" in line or "Madame, Monsieur" in line:
                c.setFont("Helvetica-Bold", 11)
                c.drawString(MARGIN_LEFT, y, line)
                c.setFont("Helvetica", 11)
            else:
                c.drawString(MARGIN_LEFT, y, line)
            
            y -= LINE_HEIGHT
        
        c.save()
        return file_path
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération de la lettre PDF : {e}")
        return None


# ==============================================================
# 🔧 FONCTION DE GÉNÉRATION POUR CV OPTIMISÉ
# ==============================================================

def generate_cv_pdf(
    cv_text: str,
    job_title: str,
    user_name: str
) -> Optional[str]:
    """
    🎯 Génère un PDF pour un CV optimisé.
    
    Args:
        cv_text: Texte du CV
        job_title: Titre du poste (pour le nom du fichier)
        user_name: Nom du candidat
    
    Returns:
        str: Chemin du PDF généré
    """
    try:
        # Créer un nom de fichier unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = job_title.replace(' ', '_').replace('/', '_')
        safe_name = user_name.replace(' ', '_')
        filename = f"CV_optimise_{safe_name}_{safe_title}_{timestamp}.pdf"
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        
        # Créer le canvas
        c = canvas.Canvas(file_path, pagesize=PAGE_SIZE)
        c.setFont("Helvetica", 10)
        
        y = PAGE_HEIGHT - MARGIN_TOP
        lines = cv_text.split("\n")
        
        for line in lines:
            if y < MARGIN_BOTTOM:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = PAGE_HEIGHT - MARGIN_TOP
            
            # Mettre en gras les titres de section
            if line.strip().startswith("###") or line.strip().endswith(":") or line.isupper():
                c.setFont("Helvetica-Bold", 11)
                # Enlever les marqueurs ###
                clean_line = line.replace("###", "").strip()
                c.drawString(MARGIN_LEFT, y, clean_line)
                c.setFont("Helvetica", 10)
            else:
                c.drawString(MARGIN_LEFT, y, line)
            
            y -= LINE_HEIGHT
        
        c.save()
        return file_path
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du CV PDF : {e}")
        return None


# ==============================================================
# 🔧 FONCTION POUR GÉNÉRER UN PACK COMPLET
# ==============================================================

def generate_application_pack(
    cover_letter: str,
    cv_text: str,
    job_title: str,
    company: str,
    user_name: str
) -> Dict[str, Optional[str]]:
    """
    🎯 Génère un pack complet (lettre + CV) au format PDF.
    
    Args:
        cover_letter: Texte de la lettre de motivation
        cv_text: Texte du CV
        job_title: Titre du poste
        company: Nom de l'entreprise
        user_name: Nom du candidat
    
    Returns:
        dict: Dictionnaire avec les chemins des fichiers
    """
    result = {
        "cover_letter_pdf": None,
        "cv_pdf": None
    }
    
    # Générer la lettre
    result["cover_letter_pdf"] = generate_letter_pdf(
        cover_letter, job_title, company, user_name
    )
    
    # Générer le CV
    result["cv_pdf"] = generate_cv_pdf(cv_text, job_title, user_name)
    
    return result


# ==============================================================
# 📝 TEST (si exécuté directement)
# ==============================================================

if __name__ == "__main__":
    # Test simple
    test_text = """Paterne Gankama
24 Square des Collines
35000 Rennes
p.gankama@gmail.com
06 41 38 92 88

27/03/2026

Metier Interim Rennes

Objet : Candidature au poste de Technicien

Madame, Monsieur,

Je vous écris pour exprimer mon vif intérêt...

Cordialement,
Paterne Gankama"""
    
    pdf_path = generate_pdf(test_text, "test")
    if pdf_path:
        print(f"✅ PDF généré : {pdf_path}")
    else:
        print("❌ Erreur lors de la génération du PDF")
        

def text_to_pdf(text: str, output_path: str) -> str:
    """
    Convertit un texte en fichier PDF.
    Alias de generate_pdf pour compatibilité.
    
    Args:
        text: Texte à convertir
        output_path: Chemin de sortie du PDF
    
    Returns:
        Chemin du PDF généré
    """
    return generate_pdf(text, output_path)