import faiss
import numpy as np
import os
import pickle

DIM = 384
FAISS_PATH = "data/index.faiss"
META_PATH = "data/meta.pkl"

index = faiss.IndexFlatL2(DIM)
metadata = []

# 🔹 NEW — embedding cache
cache = {}


def save_state():
    if index.ntotal > 0:
        faiss.write_index(index, FAISS_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print("💾 Index persisted.")


def load_state():
    global index, metadata

    if os.path.exists(FAISS_PATH):
        index = faiss.read_index(FAISS_PATH)

    if os.path.exists(META_PATH):
        with open(META_PATH, "rb") as f:
            metadata.extend(pickle.load(f))

    print("📁 Loaded persisted index:", index.ntotal)


load_state()


def store_chunks(chunks, embed_fn):

    for c in chunks:
        text = c["content"]

        # 🔹 check cache
        if text in cache:
            v = cache[text]
        else:
            emb = embed_fn(text)
            v = np.array(emb).astype("float32").reshape(1, -1)
            cache[text] = v   # 🔹 store in cache

        index.add(v)
        metadata.append(c)

    save_state()
