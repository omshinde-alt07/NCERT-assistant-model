import fitz

class PDFExtractor:
    def extract(self, path):
        doc = fitz.open(path)
        text = '\n'.join(page.get_text() for page in doc)
        doc.close()
        return text
