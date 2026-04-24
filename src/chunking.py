from dataclasses import dataclass

MIN_CHUNK_WORDS = 20

@dataclass
class Chunk:
    text: str
    chapter: str
    section: str
    content_type: str

class Chunker:
    def __init__(self, size=300, overlap=50):
        self.size = size
        self.overlap = overlap

    def chunk(self, text, chapter):
        words = text.split()
        chunks = []
        step = self.size - self.overlap
        for i in range(0, len(words), step):
            part = ' '.join(words[i:i + self.size])
            if len(part.split()) >= MIN_CHUNK_WORDS:
                chunks.append(Chunk(part, chapter, f'Section-{len(chunks) + 1}', 'concept'))
        return chunks