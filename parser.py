import fitz
from PIL import Image
import pytesseract

def extract_pdf_text(path):
    text = ""
    try:
        doc = fitz.open(path)
        for page in doc:
            t = page.get_text()
            if not t.strip():
                img = Image.frombytes("RGB", [page.rect.width, page.rect.height], page.get_pixmap(dpi=300).samples)
                t = pytesseract.image_to_string(img)
            text += t + "\n"
    except Exception as e:
        text += f"Error reading PDF: {e}"
    return text
