from rank_bm25 import BM25Okapi
class Retriever:
    def __init__(self, chunks):
        self.chunks=chunks
        self.bm25=BM25Okapi([c.text.lower().split() for c in chunks])
    def search(self, query, k=3):
        scores=self.bm25.get_scores(query.lower().split())
        ids=sorted(range(len(scores)), key=lambda i:scores[i], reverse=True)[:k]
        return [self.chunks[i] for i in ids]