# 📚 Study Assistant

A local RAG (Retrieval-Augmented Generation) tool that answers questions from your physics textbook PDFs using BM25 search and a local LLM via Ollama.

---

## How It Works

```
PDF Files → Extract Text → Clean → Chunk → BM25 Index → Retrieve → LLM → Answer
```

1. PDFs are extracted and cleaned (removes figure labels, page numbers, extra whitespace)
2. Text is split into overlapping chunks (300 words, 50-word overlap)
3. Questions are matched to the top 3 relevant chunks using BM25
4. Chunks are passed as context to a local Phi-3 model via Ollama
5. Results and latency are saved to a CSV evaluation report

---

## Project Structure

```
study_assistant/
├── main.py                  # Entry point
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
│   ├── evaluator.py         # Evaluation + CSV export
│   └── utils.py             # Helper functions
└── outputs/
    ├── preprocessing_preview.txt
    └── evaluation_results.csv
```

---

## Setup

### 1. Prerequisites

- macOS with [pyenv](https://github.com/pyenv/pyenv) installed
- [Ollama](https://ollama.com/download) installed and running

### 2. Install Python via pyenv

```bash
brew install pyenv
pyenv install 3.13.3
```

### 3. Clone and set up the project

```bash
cd study_assistant
pyenv local 3.13.3
~/.pyenv/versions/3.13.3/bin/python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Start Ollama and pull the model

```bash
ollama serve          # keep this running in a separate terminal
ollama pull phi3
```

### 5. Run

```bash
python main.py
```

---

## Sample Output

```
$ python main.py

Force is a push or pull acting on an object. It can change the state
of motion of an object — causing it to speed up, slow down, or change
direction. Force has both magnitude and direction, making it a vector
quantity. The SI unit of force is the Newton (N).

[Evaluator] Results saved to outputs/evaluation_results.csv
```

**`outputs/evaluation_results.csv`**

| question | answer | num_chunks_retrieved | top_chunk_preview | latency_seconds |
|---|---|---|---|---|
| What is force? | Force is a push or pull... | 3 | Force is defined as any interaction... | 4.21 |
| Define inertia | Inertia is the tendency of an object... | 3 | Newton's first law states that... | 3.87 |
| What is acceleration? | Acceleration is the rate of change... | 3 | When a net force acts on an object... | 4.05 |

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

To use a different model (e.g. llama3):
```bash
ollama pull llama3
```
Then update `config.py`:
```python
MODEL_NAME = "llama3"
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'fitz'`**
→ Install via: `pip install pymupdf` (not `pip install fitz`)

**`Failed to connect to Ollama`**
→ Run `ollama serve` in a separate terminal, then retry

**pip broken on macOS 26 (Tahoe)**
→ Use pyenv to build Python from source — see Setup above
