import time
import pandas as pd

class Evaluator:
    def run(self, app, questions, path):
        rows = []
        for q in questions:
            start = time.time()
            r = app.answer(q)
            elapsed = round(time.time() - start, 3)
            rows.append({
                'question': q,
                'answer': r['answer'],
                'num_chunks_retrieved': len(r['chunks']),
                'top_chunk_preview': r['chunks'][0].text[:120] if r['chunks'] else '',
                'latency_seconds': elapsed,
            })
        pd.DataFrame(rows).to_csv(path, index=False)
        print(f"[Evaluator] Results saved to {path}")
