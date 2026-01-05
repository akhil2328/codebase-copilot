import requests

# 🔹 SHORT + FAST system prompt (no fluff)
SYSTEM_PROMPT = """
You are a code assistant.
Answer strictly using ONLY the provided code.
If the answer is not in the code, say you are unsure.
Keep answers concise and clear.
"""


def ask_llm(question, ranked_chunks):

    # build clean context
    context = "\n\n".join(
        f"[FILE: {r['path']}]\n{r['content']}"
        for r in ranked_chunks
    )

    # 🔹 optimized final prompt (small = faster first token)
    prompt = f"""
{SYSTEM_PROMPT}

Context:
{context}

Question:
{question}

Answer:
"""

    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:1.5b",
            "prompt": prompt,
            "stream": False   # ⚠️ unchanged on purpose
        }
    )

    return r.json()["response"]
