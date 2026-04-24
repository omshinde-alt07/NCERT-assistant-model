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
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        for i, file in enumerate(PDF_FILES, start=8):
            pdf_path = os.path.join(base_dir, DATA_DIR, file)

            raw = self.extractor.extract(pdf_path)
            clean = self.cleaner.clean(raw)

            # Save processed text per chapter
            out_path = os.path.join(OUTPUT_DIR, f"processed_chapter_{i}.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(clean)
            print(f"[Preprocessor] Saved processed text → {out_path}")

            self.chunks.extend(
                self.chunker.chunk(clean, f"Chapter-{i}")
            )

        # Save all chunks to a single file for inspection
        chunks_path = os.path.join(OUTPUT_DIR, "all_chunks.txt")
        with open(chunks_path, "w", encoding="utf-8") as f:
            for idx, c in enumerate(self.chunks):
                f.write(f"--- Chunk {idx+1} | {c.chapter} | {c.section} ---\n")
                f.write(c.text + "\n\n")
        print(f"[Preprocessor] Saved {len(self.chunks)} chunks → {chunks_path}\n")

        self.retriever = Retriever(self.chunks)
        self.llm = LLMAnswerer(model_name=MODEL_NAME)

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

    # 10 questions with expected answers for evaluation
    qa_pairs = [
        {
            "question": "What is force?",
            "expected_answer": "Force is a push or pull on an object. It can change the state of motion of an object. Its SI unit is Newton (N)."
        },
        {
            "question": "Define inertia.",
            "expected_answer": "Inertia is the tendency of an object to resist any change in its state of rest or uniform motion."
        },
        {
            "question": "What is Newton's first law of motion?",
            "expected_answer": "An object remains at rest or in uniform motion unless acted upon by an external unbalanced force."
        },
        {
            "question": "What is Newton's second law of motion?",
            "expected_answer": "The acceleration of an object is directly proportional to the net force applied and inversely proportional to its mass. F = ma."
        },
        {
            "question": "What is Newton's third law of motion?",
            "expected_answer": "For every action there is an equal and opposite reaction."
        },
        {
            "question": "What is acceleration?",
            "expected_answer": "Acceleration is the rate of change of velocity with respect to time. It is measured in m/s²."
        },
        {
            "question": "What is momentum?",
            "expected_answer": "Momentum is the product of an object's mass and its velocity. p = mv. Its SI unit is kg·m/s."
        },
        {
            "question": "What is the SI unit of force?",
            "expected_answer": "The SI unit of force is Newton (N)."
        },
        {
            "question": "What is uniform motion?",
            "expected_answer": "Uniform motion is when an object covers equal distances in equal intervals of time in a straight line."
        },
        {
            "question": "What is the difference between speed and velocity?",
            "expected_answer": "Speed is the distance covered per unit time and is a scalar. Velocity is displacement per unit time and is a vector (has direction)."
        },
    ]

    Evaluator().run(
        app,
        qa_pairs,
        os.path.join(OUTPUT_DIR, "evaluation_results.csv")
    )
