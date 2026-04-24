# 📚 NCERT Study Assistant

A local RAG (Retrieval-Augmented Generation) tool that answers questions from NCERT physics textbook PDFs using BM25 keyword search and a local LLM via Ollama.

---

## How It Works

```
PDF Files → Extract Text → Clean → Chunk → BM25 Index → Retrieve Top-3 → LLM → Answer
```

1. PDFs are extracted and cleaned (removes figure labels, page numbers, extra whitespace)
2. Text is split into overlapping chunks (300 words, 50-word overlap)
3. Questions are matched to the top 3 relevant chunks using BM25
4. Chunks are passed as context to a local Phi-3 model via Ollama
5. Answers are graded as CORRECT / INCORRECT against expected answers
6. Full results with latency are saved to a CSV evaluation report

---

## Project Structure

```
NCERT-assistant-model/
├── main.py                  # Entry point + 10 evaluation questions
├── config.py                # Settings (chunk size, model, paths)
├── requirements.txt
├── data/
│   ├── ch08_motion.pdf
│   └── ch09_force.pdf
├── src/
│   ├── extractor.py         # PDF text extraction (PyMuPDF)
│   ├── preprocessing.py     # Text cleaning
│   ├── chunking.py          # Overlapping word chunker
│   ├── retriever.py         # BM25 search
│   ├── llm.py               # Ollama LLM answering
│   ├── evaluator.py         # Correctness grading + CSV export
│   └── utils.py             # Helper functions
└── outputs/
    ├── processed_chapter_8.txt
    ├── processed_chapter_9.txt
    ├── all_chunks.txt
    └── evaluation_results.csv
```

---

## Setup

### 1. Install Python via pyenv (recommended on macOS)

> ⚠️ If you're on macOS 26 (Tahoe) or any beta OS, Homebrew Python has a broken `libexpat`. Use pyenv to build Python from source instead.

```bash
brew install pyenv
pyenv install 3.13.3
```

### 2. Clone and set up the project

```bash
git clone https://github.com/omshinde-alt07/NCERT-assistant-model.git
cd NCERT-assistant-model

pyenv local 3.13.3
~/.pyenv/versions/3.13.3/bin/python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Start Ollama and pull the model

```bash
# In a separate terminal:
ollama serve

# Pull the model (first time only):
ollama pull phi3
```

### 4. Run

```bash
python main.py
```

---

## Sample Console Output

```
[Preprocessor] Saved processed text → outputs/processed_chapter_8.txt
[Preprocessor] Saved processed text → outputs/processed_chapter_9.txt
[Preprocessor] Saved 61 chunks → outputs/all_chunks.txt

============================================================
  Running evaluation on 10 questions
============================================================

Q1: What is force?
  Expected : Force is a push or pull on an object...
  Got      : I don't know from context.
  ❌ INCORRECT — Retrieved chunks were from wrong chapter

Q2: Define inertia.
  Expected : Inertia is the tendency of an object to resist...
  Got      : Inertia refers to the property of matter that describes its resistance...
  ✅ CORRECT — Accurate, includes relevant concepts and Newton's first law

Q3: What is Newton's first law of motion?
  Expected : An object remains at rest or in uniform motion...
  Got      : Newton's first law states that an object at rest will stay at rest...
  ❌ INCORRECT — Includes extra details beyond scope; core concept not clearly stated

...

============================================================
  Score: 6/10 correct (60.0%)
  Results saved to outputs/evaluation_results.csv
============================================================
```

---

## Evaluation Results

Tested on **10 NCERT physics questions** from chapters on Motion and Force.

| # | Question | Verdict | Notes |
|---|---|---|---|
| 1 | What is force? | ❌ INCORRECT | Retrieved wrong chapter chunks |
| 2 | Define inertia | ✅ CORRECT | Accurate with Newton's 1st law reference |
| 3 | What is Newton's first law? | ❌ INCORRECT | Answer too verbose, core concept lost |
| 4 | What is Newton's second law? | ✅ CORRECT | F=ma explained correctly |
| 5 | What is Newton's third law? | ✅ CORRECT | Exact match |
| 6 | What is acceleration? | ✅ CORRECT | Correct with units and vector property |
| 7 | What is momentum? | ❌ INCORRECT | Retrieved wrong chapter chunks |
| 8 | What is the SI unit of force? | ✅ CORRECT | Exact: Newton (N) |
| 9 | What is uniform motion? | ❌ INCORRECT | Retrieved wrong chapter chunks |
| 10 | Speed vs velocity difference | ✅ CORRECT | Scalar/vector distinction correct |

**Final Score: 6 / 10 (60%)**

### Why 4 questions failed

Questions about force, momentum, and uniform motion retrieved chunks from chemistry chapters (atoms, compounds) instead of the motion/force chapters. This is a **BM25 retrieval issue** — the keyword overlap was low, so the wrong chunks were returned. Improving this requires either better keyword weighting or switching to embedding-based (semantic) retrieval.

---

## Configuration

Edit `config.py` to change behaviour:

| Setting | Default | Description |
|---|---|---|
| `CHUNK_SIZE` | `300` | Words per chunk |
| `OVERLAP` | `50` | Overlap between chunks |
| `TOP_K` | `3` | Chunks retrieved per query |
| `MODEL_NAME` | `"phi3"` | Ollama model to use |
| `PDF_FILES` | `[ch08, ch09]` | PDFs to index |

To use a different model:
```bash
ollama pull llama3
```
Then in `config.py`:
```python
MODEL_NAME = "llama3"
```

---

## Known Issues & Next Steps

- **BM25 retrieval is keyword-based** — questions with low keyword overlap with the PDF return wrong chunks. Switching to semantic search (e.g. sentence-transformers + FAISS) would improve accuracy significantly.
- **Phi-3 via Ollama can be slow** — 5–10s per question on CPU. Use a GPU or a smaller model for faster responses.
- **Grader prompt leakage** — the evaluator LLM occasionally produces extra reasoning in its verdict. This is handled gracefully but could be tightened with stricter prompting.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `No module named 'fitz'` | Run `pip install pymupdf` (not `pip install fitz`) |
| `Failed to connect to Ollama` | Run `ollama serve` in a separate terminal |
| `pip broken on macOS 26` | Use pyenv — see Setup section above |
| Wrong answers / "I don't know" | Check `outputs/all_chunks.txt` — relevant content may not be in the indexed PDFs |
