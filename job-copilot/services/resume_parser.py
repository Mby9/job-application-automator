import io
from pypdf import PdfReader
from docx import Document

def parse_resume_file(contents: bytes, filename: str) -> str:
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    text = ""
    
    try:
        if ext == "pdf":
            reader = PdfReader(io.BytesIO(contents))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        elif ext in ["docx", "doc"]:
            # python-docx directly supports .docx
            doc = Document(io.BytesIO(contents))
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            # Fallback for .txt or unknown
            text = contents.decode("utf-8", errors="ignore")
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            text = contents.decode("utf-8", errors="ignore")
        except:
            pass
            
    import re
    text = re.sub(r'\s+', ' ', text).strip()
    return text
