import requests

SYSTEM_PROMPT = """
You are a senior software engineer.

Rules:
- Answer only from the provided code context.
- If information is missing, say "I could not find that in the indexed code."
- Keep answers concise.
- Mention file names when relevant.
- Focus on architecture, functions, APIs, classes, and implementation details.
"""


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "qwen2.5:1.5b"

MAX_CONTEXT_PER_CHUNK = 500


def ask_llm(question, ranked_chunks):

    # -----------------------------
    # Build compact context
    # -----------------------------

    context = "\n\n".join(
        f"[FILE: {chunk['path']}]\n{chunk['content'][:MAX_CONTEXT_PER_CHUNK]}"
        for chunk in ranked_chunks
    )

    prompt = f"""
{SYSTEM_PROMPT}

CODE CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 250
                }
            },
            timeout=60
        )

        data = response.json()

        if "response" not in data:
            return f"LLM Error: {data}"

        return data["response"].strip()

    except requests.exceptions.Timeout:
        return "The AI model took too long to respond."

    except Exception as e:
        return f"LLM Error: {str(e)}"
