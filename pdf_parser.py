from PyPDF2 import PdfReader


def pdf_to_text(path_to_pdf: str) -> str:
    reader = PdfReader(path_to_pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
