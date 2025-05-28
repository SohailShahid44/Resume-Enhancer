import pdfplumber
import tempfile
import os

def extract_text_from_pdf(uploaded_file) -> str:
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        with pdfplumber.open(tmp_file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    finally:
        os.unlink(tmp_file_path)

    return text.strip()
