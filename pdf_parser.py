from __future__ import annotations
from typing import List

def extract_pdf_pages_text(uploaded_file) -> List[str]:
    """
    Extract text per page from a Streamlit UploadedFile (PDF).
    Returns a list of page strings. If extraction fails, returns [""].
    """
    data = uploaded_file.read()
    # Reset pointer so Streamlit can re-read if needed
    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    try:
        from PyPDF2 import PdfReader
        import io
        reader = PdfReader(io.BytesIO(data))
        pages = []
        for p in reader.pages:
            txt = p.extract_text() or ""
            pages.append(txt)
        return pages if pages else [""]
    except Exception:
        # Minimal fallback: whole-doc extraction via pdfminer if available
        try:
            import io
            from pdfminer.high_level import extract_text
            txt = extract_text(io.BytesIO(data)) or ""
            return [txt]
        except Exception:
            return [""]
