import time
import pandas as pd
import ollama


GRADER_PROMPT = """You are a strict answer evaluator for a physics textbook Q&A system.

Question: {question}
Expected Answer: {expected}
Student Answer: {answer}

Does the student answer correctly address the question and match the expected answer in meaning?
Reply with ONLY one word: CORRECT or INCORRECT, then a dash, then a one-line reason.
Example: CORRECT - Accurately defines force as a push or pull with correct units.
Example: INCORRECT - Confuses force with energy and omits mention of Newton.
"""


class Evaluator:
    def __init__(self, model_name="phi3"):
        self.model_name = model_name

    def _grade(self, question, expected, answer):
        if answer.strip().startswith("[LLM Error]") or answer == "I don't know":
            return "INCORRECT", "LLM unavailable or no answer returned"
        try:
            prompt = GRADER_PROMPT.format(
                question=question,
                expected=expected,
                answer=answer
            )
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response["message"]["content"].strip()
            if " - " in raw:
                verdict, reason = raw.split(" - ", 1)
            else:
                verdict, reason = raw, ""
            verdict = verdict.strip().upper()
            if verdict not in ("CORRECT", "INCORRECT"):
                verdict = "INCORRECT"
            return verdict, reason.strip()
        except Exception as e:
            return "ERROR", str(e)

    def run(self, app, qa_pairs, path):
        """
        qa_pairs: list of dicts with keys 'question' and 'expected_answer'
        """
        rows = []
        correct_count = 0

        print(f"\n{'='*60}")
        print(f"  Running evaluation on {len(qa_pairs)} questions")
        print(f"{'='*60}\n")

        for i, qa in enumerate(qa_pairs, 1):
            question = qa["question"]
            expected = qa["expected_answer"]

            start = time.time()
            r = app.answer(question)
            elapsed = round(time.time() - start, 3)

            answer = r["answer"]
            verdict, reason = self._grade(question, expected, answer)

            if verdict == "CORRECT":
                correct_count += 1
                icon = "✅"
            else:
                icon = "❌"

            print(f"Q{i}: {question}")
            print(f"  Expected : {expected[:100]}")
            print(f"  Got      : {answer[:100]}")
            print(f"  {icon} {verdict} — {reason}")
            print()

            rows.append({
                "question": question,
                "expected_answer": expected,
                "model_answer": answer,
                "verdict": verdict,
                "reason": reason,
                "num_chunks_retrieved": len(r["chunks"]),
                "top_chunk_preview": r["chunks"][0].text[:150] if r["chunks"] else "",
                "latency_seconds": elapsed,
            })

        df = pd.DataFrame(rows)
        df.to_csv(path, index=False)

        accuracy = round(correct_count / len(qa_pairs) * 100, 1)
        print(f"{'='*60}")
        print(f"  Score: {correct_count}/{len(qa_pairs)} correct ({accuracy}%)")
        print(f"  Results saved to {path}")
        print(f"{'='*60}\n")
