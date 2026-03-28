"""
=====================================================================
📄 CV EXTRACTION SERVICE - EXTRAIRE LES INFOS D'UN CV PDF
=====================================================================

🎯 RÔLE DE CE FICHIER :
Ce fichier contient les fonctions pour extraire des informations d'un CV au format PDF.
- Extraire le texte brut du PDF
- Extraire les coordonnées (nom, email, téléphone, adresse)

📚 POUR UN DÉBUTANT :
- Un PDF est comme une image de document. On ne peut pas lire le texte directement.
- PyPDF2 est une bibliothèque qui permet de "lire" le texte caché dans le PDF.
- Les expressions régulières (regex) permettent de chercher des motifs dans le texte.

=====================================================================
"""

# ==============================================================
# 📦 IMPORT DES BIBLIOTHÈQUES
# ==============================================================
import PyPDF2      # Pour lire les fichiers PDF
import re          # Pour les expressions régulières (chercher des motifs dans le texte)


# ==============================================================
# 🔧 FONCTION 1 : EXTRAIRE LE TEXTE D'UN PDF
# ==============================================================

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrait le texte brut d'un fichier PDF.
    
    📚 EXPLICATION POUR DÉBUTANT :
    Cette fonction ouvre un fichier PDF, lit chaque page, et récupère le texte.
    Le texte est ensuite nettoyé et retourné sous forme de chaîne de caractères.
    
    Args:
        pdf_path (str): Le chemin du fichier PDF (ex: "storage/cv/mon_cv.pdf")
    
    Returns:
        str: Le texte extrait du PDF (ou une chaîne vide en cas d'erreur)
    
    Exemple:
        >>> texte = extract_text_from_pdf("mon_cv.pdf")
        >>> print(texte[:100])  # Affiche les 100 premiers caractères
        "Paterne GANKAMA\n123 rue de Paris\n0612345678\npaterne@email.com..."
    """
    
    # Variable qui va contenir tout le texte extrait
    texte_complet = ""

    try:
        # ==========================================================
        # ÉTAPE 1 : Ouvrir le fichier PDF
        # ==========================================================
        # open() : ouvre le fichier
        # "rb" : mode lecture binaire (read binary) - nécessaire pour les PDF
        # with : garantit que le fichier sera bien fermé après utilisation
        with open(pdf_path, "rb") as fichier:
            
            # ==========================================================
            # ÉTAPE 2 : Créer un lecteur PDF
            # ==========================================================
            # PyPDF2.PdfReader() : crée un objet qui sait lire le PDF
            lecteur_pdf = PyPDF2.PdfReader(fichier)
            
            # ==========================================================
            # ÉTAPE 3 : Vérifier que le PDF n'est pas vide
            # ==========================================================
            # lecteur_pdf.pages : liste des pages du PDF
            # Si la liste est vide, le PDF ne contient pas de texte
            if not lecteur_pdf.pages:
                print("❌ PDF vide ou illisible")
                return ""  # Retourne une chaîne vide
            
            # ==========================================================
            # ÉTAPE 4 : Parcourir chaque page et extraire le texte
            # ==========================================================
            # enumerate() : permet d'avoir le numéro de page (i) et la page elle-même
            for i, page in enumerate(lecteur_pdf.pages):
                try:
                    # extraire le texte de la page
                    texte_page = page.extract_text()
                    
                    # Si du texte a été extrait, on l'ajoute au texte complet
                    if texte_page:
                        texte_complet += texte_page + "\n"  # On ajoute un retour à la ligne
                
                except Exception as e:
                    # En cas d'erreur sur une page, on continue avec la suivante
                    print(f"⚠️ Erreur à la page {i} : {e}")

    except Exception as e:
        # Si le fichier n'existe pas ou est corrompu
        print("❌ Erreur lors de l'ouverture du PDF :", e)
        return ""  # Retourne une chaîne vide

    # ==========================================================
    # ÉTAPE 5 : Nettoyer le texte (enlever les espaces inutiles)
    # ==========================================================
    # strip() : enlève les espaces au début et à la fin
    texte_complet = texte_complet.strip()

    # ==========================================================
    # ÉTAPE 6 : Vérifier que du texte a bien été extrait
    # ==========================================================
    if not texte_complet:
        print("⚠️ Aucun texte extrait (le PDF est peut-être une image scannée)")

    return texte_complet


# ==============================================================
# 🔧 FONCTION 2 : EXTRAIRE LES COORDONNÉES DU TEXTE
# ==============================================================

# ==============================================================
# 🔧 FONCTION 2 : EXTRAIRE LES COORDONNÉES
# ==============================================================

def extract_contact_info(texte_cv: str) -> dict:
    """
    Extrait les coordonnées depuis user_config.py (pas du CV).
    Cela garantit des coordonnées propres et sans messages de test.
    
    📚 EXPLICATION :
    Au lieu d'extraire du CV qui peut contenir des données de test,
    on utilise le fichier de configuration user_config.py qui contient
    les vraies coordonnées de l'utilisateur.
    
    Args:
        texte_cv (str): Le texte du CV (non utilisé, conservé pour compatibilité)
    
    Returns:
        dict: Un dictionnaire avec les coordonnées depuis user_config
    """
    try:
        # Importer la configuration utilisateur
        from app.core.user_config import USER_CONFIG
        
        return {
            "name": USER_CONFIG.get("name", ""),
            "email": USER_CONFIG.get("email", ""),
            "phone": USER_CONFIG.get("phone", ""),
            "address": USER_CONFIG.get("address", "")
        }
    except ImportError:
        # Fallback si le module n'est pas trouvé
        print("⚠️ user_config.py non trouvé, utilisation de l'extraction standard")
        
        # Code d'extraction original en fallback
        lignes = texte_cv.split("\n")
        
        # Extraire le nom
        nom = ""
        for ligne in lignes:
            if ligne.strip():
                nom = ligne.strip()
                break
        
        # Extraire l'email
        motif_email = r'[\w\.-]+@[\w\.-]+'
        email_match = re.search(motif_email, texte_cv)
        email = email_match.group(0) if email_match else ""
        
        # Extraire le téléphone
        motif_telephone = r'(\+?\d[\d\s]{8,})'
        telephone_match = re.search(motif_telephone, texte_cv)
        telephone = telephone_match.group(0) if telephone_match else ""
        
        # Extraire l'adresse
        adresse = ""
        mots_cles_adresse = ['rue', 'avenue', 'boulevard', 'place', 'impasse', 'allée', 'chemin', 'square']
        
        for ligne in lignes:
            ligne_minuscules = ligne.lower()
            for mot_cle in mots_cles_adresse:
                if mot_cle in ligne_minuscules:
                    adresse = ligne.strip()
                    break
            if adresse:
                break
        
        return {
            "name": nom,
            "email": email,
            "phone": telephone,
            "address": adresse
        }


# ==============================================================
# 🔧 FONCTION 3 : NETTOYER UN NUMÉRO DE TÉLÉPHONE (optionnel)
# ==============================================================

def clean_phone_number(phone: str) -> str:
    """
    Nettoie un numéro de téléphone pour n'avoir que les chiffres.
    
    📚 EXPLICATION :
    Transforme "06 12 34 56 78" ou "06.12.34.56.78" en "0612345678"
    
    Args:
        phone (str): Numéro de téléphone brut
    
    Returns:
        str: Numéro nettoyé (uniquement les chiffres)
    """
    # re.sub() : remplace tout ce qui n'est pas un chiffre par une chaîne vide
    # [^0-9] : tout ce qui n'est pas entre 0 et 9
    return re.sub(r'[^0-9]', '', phone)


# ==============================================================
# 🔧 FONCTION 4 : FORMATER LE NOM (optionnel)
# ==============================================================

def format_name(name: str) -> str:
    """
    Formate le nom pour avoir la première lettre de chaque mot en majuscule.
    
    📚 EXPLICATION :
    Transforme "paterne gankama" en "Paterne Gankama"
    
    Args:
        name (str): Nom brut
    
    Returns:
        str: Nom formaté
    """
    # title() : met la première lettre de chaque mot en majuscule
    return name.title()


