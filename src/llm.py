import ollama

class LLMAnswerer:
    def __init__(self, model_name="phi3"):
        self.model_name = model_name

    def generate(self, question, chunks):
        context = "\n\n".join(c.text for c in chunks)

        prompt = f"""
Answer only from context.
If answer not found, say: I don't know.

Context:
{context}

Question:
{question}
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response["message"]["content"]