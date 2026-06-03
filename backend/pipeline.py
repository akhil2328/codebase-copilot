from repo_loader import clone_repo
from code_reader import read_code
from chunker import chunk_code
from embeddings import embed_text
from vector_store import store_chunks, clear_index
from search import search
from llm import ask_llm
from firebase_db import log_question

# ----------------------------------------
# Query Rewrite
# ----------------------------------------


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


# ----------------------------------------
# Index State
# ----------------------------------------

index_built = False


# ----------------------------------------
# Lightweight Chat Memory
# ----------------------------------------

history = []


# ----------------------------------------
# Build Index
# ----------------------------------------

def build_index(url):

    global index_built

    index_built = False

    print("STEP 0: clearing old index")
    clear_index()

    print("STEP 1: cloning repository")
    clone_repo(url)

    print("STEP 2: reading files")
    files = read_code()

    print("STEP 3: chunking files")
    chunks = chunk_code(files)

    print("STEP 4: generating embeddings + storing")
    store_chunks(chunks, embed_text)

    index_built = True

    print("✅ INDEX BUILT SUCCESSFULLY")


# ----------------------------------------
# Answer User Question
# ----------------------------------------

def answer(q):

    global history

    if not q.strip():
        return "Please enter a question."

    if not index_built:
        return "Error: No repository indexed yet"

    rewritten_query = rewrite(q)

    ranked = search(
        rewritten_query,
        embed_text
    )
    print("SEARCH RESULTS:", len(ranked))
    if ranked:
        print("FIRST RESULT:", ranked[0]["path"])

    if not ranked:
        return "Sorry — no relevant code found."

    # Faster than 5 chunks
    ranked = ranked[:2]

    # ----------------------------------------
    # Conversation Memory
    # ----------------------------------------

    history_text = "\n".join(
        f"Q: {h['q']}\nA: {h['a']}"
        for h in history[-2:]
    )

    prompt_question = f"""
Previous conversation:
{history_text}

Current question:
{q}
"""

    answer_text = ask_llm(
        prompt_question,
        ranked
    )

    # ----------------------------------------
    # Save Memory
    # ----------------------------------------

    history.append({
        "q": q,
        "a": answer_text
    })

    # Keep only latest 3
    history[:] = history[-3:]

    # ----------------------------------------
    # Firebase Logging
    # ----------------------------------------

    try:
        log_question(
            q,
            answer_text
        )
    except Exception:
        pass

    return answer_text
