from pypdf import PdfReader


def read_pdf_file(source):
    """Extract readable text from all pages of a PDF file or file-like object."""
    reader = PdfReader(source)
    page_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(page_text)
