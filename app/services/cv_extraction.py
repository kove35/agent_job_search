import PyPDF2

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrait le texte brut d'un CV PDF.
    """
    text = ""

    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)

        for page in reader.pages:
            text += page.extract_text() + "\n"

    return text.strip()
import PyPDF2

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrait le texte brut d'un CV PDF.
    """
    text = ""

    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)

        for page in reader.pages:
            text += page.extract_text() + "\n"

    return text.strip()
