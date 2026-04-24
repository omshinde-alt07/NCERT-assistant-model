import re

class TextCleaner:
    def clean(self, text):
        text = re.sub(r'Fig\.?\s*\d+(\.\d+)*', ' ', text, flags=re.I)
        text = re.sub(r'Page\s*\d+', ' ', text, flags=re.I)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()