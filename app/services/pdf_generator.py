from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import uuid

# 📁 dossier sortie PDF
OUTPUT_FOLDER = "generated_docs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def generate_pdf(text, filename_prefix="doc"):
    """
    🎯 Génère un PDF simple à partir de texte

    🧠 ALGO :
    texte →
        découpe lignes →
            écrit ligne par ligne →
                sauvegarde PDF
    """

    file_id = str(uuid.uuid4())
    file_path = os.path.join(OUTPUT_FOLDER, f"{filename_prefix}_{file_id}.pdf")

    c = canvas.Canvas(file_path, pagesize=A4)

    width, height = A4
    y = height - 40

    for line in text.split("\n"):
        c.drawString(40, y, line)
        y -= 15

        if y < 40:
            c.showPage()
            y = height - 40

    c.save()

    return file_path 