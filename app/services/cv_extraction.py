# =========================================================
# 📄 CV EXTRACTION SERVICE
# =========================================================
# 🎯 RÔLE :
# Extraire le texte d’un CV PDF
#
# 👉 utilisé par :
# profile_extractor → extract_profile_from_cv()
#
# 🔥 FLOW :
# PDF → texte → profil → scoring
#
# =========================================================


# =========================================================
# 🔹 IMPORTS
# =========================================================
import PyPDF2


# =========================================================
# 🔹 EXTRACTION TEXTE PDF
# =========================================================
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrait le texte brut d'un fichier PDF

    INPUT :
    - pdf_path : chemin du fichier PDF

    OUTPUT :
    - texte brut du CV
    """

    text = ""

    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            # ⚠️ certains PDF peuvent être corrompus
            if not reader.pages:
                print("❌ PDF vide ou illisible")
                return ""

            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

                except Exception as e:
                    print(f"⚠️ Erreur page {i} :", e)

    except Exception as e:
        print("❌ Erreur ouverture PDF :", e)
        return ""

    # nettoyage final
    text = text.strip()

    if not text:
        print("⚠️ Aucun texte extrait (PDF image ?)")

    return text