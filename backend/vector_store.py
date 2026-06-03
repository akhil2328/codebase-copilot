import faiss
import numpy as np
import os
import pickle

DIM = 384

DATA_DIR = "data"
FAISS_PATH = os.path.join(DATA_DIR, "index.faiss")
META_PATH = os.path.join(DATA_DIR, "meta.pkl")

os.makedirs(DATA_DIR, exist_ok=True)

index = faiss.IndexFlatL2(DIM)
metadata = []

# In-memory embedding cache
cache = {}


def save_state():
    """Persist FAISS index + metadata"""

    if index.ntotal > 0:
        faiss.write_index(index, FAISS_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print(f"💾 Index persisted ({index.ntotal} vectors)")


def load_state():
    """Load existing FAISS index"""

    global index, metadata

    if os.path.exists(FAISS_PATH):
        index = faiss.read_index(FAISS_PATH)

    if os.path.exists(META_PATH):
        with open(META_PATH, "rb") as f:
            metadata = pickle.load(f)

    print(f"📁 Loaded persisted index: {index.ntotal}")


def clear_index():
    """
    Clears current index before indexing a new repository.
    Prevents vectors from accumulating forever.
    """

    global index, metadata, cache

    index = faiss.IndexFlatL2(DIM)

    metadata.clear()
    cache.clear()

    if os.path.exists(FAISS_PATH):
        os.remove(FAISS_PATH)

    if os.path.exists(META_PATH):
        os.remove(META_PATH)

    print("🗑️ Old index cleared")


def store_chunks(chunks, embed_fn):
    """
    Convert chunks to embeddings and store in FAISS.
    """

    added = 0

    for chunk in chunks:

        text = chunk["content"]

        if not text.strip():
            continue

        if text in cache:
            vector = cache[text]

        else:
            embedding = embed_fn(text)

            vector = (
                np.array(embedding)
                .astype("float32")
                .reshape(1, -1)
            )

            cache[text] = vector

        index.add(vector)
        metadata.append(chunk)

        added += 1

    save_state()

    print(f"✅ Added {added} chunks")
    print(f"📊 Total vectors: {index.ntotal}")


load_state()
