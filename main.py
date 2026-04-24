import os
from config import *
from src.extractor import PDFExtractor
from src.preprocessing import TextCleaner
from src.chunking import Chunker
from src.retriever import Retriever
from src.llm import LLMAnswerer
from src.evaluator import Evaluator


class StudyAssistant:
    def __init__(self):
        self.extractor = PDFExtractor()
        self.cleaner = TextCleaner()
        self.chunker = Chunker(CHUNK_SIZE, OVERLAP)
        self.chunks = []

        base_dir = os.path.dirname(os.path.abspath(__file__))

        for i, file in enumerate(PDF_FILES, start=8):
            pdf_path = os.path.join(base_dir, DATA_DIR, file)

            raw = self.extractor.extract(pdf_path)
            clean = self.cleaner.clean(raw)

            self.chunks.extend(
                self.chunker.chunk(clean, f"Chapter-{i}")
            )

        self.retriever = Retriever(self.chunks)
        self.llm = LLMAnswerer(model_name=MODEL_NAME)

    def preview(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        file_path = os.path.join(
            OUTPUT_DIR,
            "preprocessing_preview.txt"
        )

        with open(file_path, "w", encoding="utf-8") as f:
            for c in self.chunks[:3]:
                f.write(c.chapter + "\n")
                f.write(c.text[:800] + "\n\n")

    def answer(self, question):
        top = self.retriever.search(question, TOP_K)

        try:
            ans = self.llm.generate(question, top)
        except Exception as e:
            print(f"[LLM Error] {e}")
            ans = top[0].text if top else "I don't know"

        return {
            "answer": ans,
            "chunks": top
        }


if __name__ == "__main__":
    app = StudyAssistant()

    app.preview()

    print(app.answer("What is force?")["answer"])

    questions = [
        "What is force?",
        "Define inertia",
        "What is acceleration?"
    ]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    Evaluator().run(
        app,
        questions,
        os.path.join(
            OUTPUT_DIR,
            "evaluation_results.csv"
        )
    )