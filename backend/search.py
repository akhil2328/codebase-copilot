import numpy as np
from vector_store import index, metadata


# -------------------------------
# 🔍 Keyword booster (NEW BUT SAFE)
# -------------------------------
def keyword_rank(query):
    """
    Lightweight keyword scoring.
    Does NOT modify existing vector search behavior.
    Returns up to 3 extra results.
    """

    q = query.lower()
    scored = []

    for c in metadata:
        text = c.get("content", "").lower()

        # match whole query + individual words
        score = text.count(q) + sum(w in text for w in q.split())

        if score > 0:
            scored.append((score, c))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [c for _, c in scored[:3]]


# -------------------------------
# ⭐ MAIN SEARCH (UNCHANGED BASE + IMPROVED)
# -------------------------------
def search(query, embed_fn, k=5):

    # if index empty → return nothing (same as before)
    if index.ntotal == 0:
        return []

    # ---- existing semantic search (UNCHANGED) ----
    vec = np.array(embed_fn(query)).astype("float32").reshape(1, -1)
    distances, indices = index.search(vec, k)

    semantic_results = []

    for idx in indices[0]:
        if idx < len(metadata):
            semantic_results.append(metadata[idx])

    # ---- NEW: add keyword-ranked matches ----
    keyword_results = keyword_rank(query)

    # ---- merge + dedupe while preserving priority ----
    all_results = []
    seen = set()

    for c in semantic_results + keyword_results:
        p = c.get("path")
        if p and p not in seen:
            seen.add(p)
            all_results.append(c)

    # keep top-4 max
    return all_results[:4]
