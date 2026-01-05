from repo_loader import clone_repo
from code_reader import read_code
from chunker import chunk_code
from embeddings import embed_text
from vector_store import store_chunks
from search import search
from llm import ask_llm
from firebase_db import log_question
from vector_store import metadata, index


# ------------------------------------------------
# 🔍 QUERY REWRITE
# ------------------------------------------------
def rewrite(q):
    q = q.lower()

    synonyms = {
        "auth": "authentication",
        "login": "sign in",
        "logout": "sign out",
        "db": "database",
        "repo": "repository",
        "func": "function",
        "params": "parameters",
    }

    for k, v in synonyms.items():
        q = q.replace(k, v)

    return q


# ------------------------------------------------
# 📦 INDEX STATE
# ------------------------------------------------
index_built = False


# ------------------------------------------------
# 🧠 LIGHTWEIGHT CHAT MEMORY (NEW)
# ------------------------------------------------
history = []   # <-- this stores the last replies only


def build_index(url):
    global index_built
    index_built = False

    clone_repo(url)

    files = read_code()

    chunks = chunk_code(files)

    store_chunks(chunks, embed_text)

    index_built = True


# ------------------------------------------------
# 🤖 ANSWER USER QUESTION
# ------------------------------------------------
def answer(q):
    global history

    if not index_built:
        return "Error: No repository indexed yet"

    rq = rewrite(q)

    ranked = search(rq, embed_text)

    if not ranked:
        return "Sorry — no relevant code found."

    ranked = ranked[:5]

    # ---------- build small conversation memory ----------
    history_text = "\n".join(
        f"Q: {h['q']}\nA: {h['a']}"
        for h in history[-2:]   # last 2 QA pairs only
    )

    # ---------- pass conversation + real context ----------
    prompt_question = f"""
Previous conversation:
{history_text}

Current question:
{q}
"""

    ans = ask_llm(prompt_question, ranked)

    # ---------- store answer for future ----------
    history.append({"q": q, "a": ans})
    history[:] = history[-5:]   # keep only last 5

    try:
        log_question(q, ans)
    except:
        pass

    return ans
