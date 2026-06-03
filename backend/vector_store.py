import faiss
import numpy as np
import os
import pickle

DIM = 384

DATA_DIR = "data"
FAISS_PATH = os.path.join(DATA_DIR, "index.faiss")
META_PATH = os.path.join(DATA_DIR, "meta.pkl")

os.makedirs(DATA_DIR, exist_ok=True)

# ONE shared FAISS object
index = faiss.IndexFlatL2(DIM)

metadata = []

cache = {}


def save_state():

    if index.ntotal > 0:
        faiss.write_index(index, FAISS_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print(f"💾 Index persisted ({index.ntotal} vectors)")


def load_state():

    global metadata

    # IMPORTANT:
    # keep same FAISS object reference
    if os.path.exists(FAISS_PATH):

        loaded_index = faiss.read_index(
            FAISS_PATH
        )

        if loaded_index.ntotal > 0:

            vectors = loaded_index.reconstruct_n(
                0,
                loaded_index.ntotal
            )

            index.add(vectors)

    if os.path.exists(META_PATH):

        with open(META_PATH, "rb") as f:
            metadata.clear()
            metadata.extend(
                pickle.load(f)
            )

    print(
        f"📁 Loaded persisted index: {index.ntotal}"
    )


def clear_index():
    """
    Clear existing vectors.
    KEEP SAME OBJECT.
    """

    global metadata, cache

    index.reset()

    metadata.clear()

    cache.clear()

    if os.path.exists(FAISS_PATH):
        os.remove(FAISS_PATH)

    if os.path.exists(META_PATH):
        os.remove(META_PATH)

    print("🗑️ Old index cleared")


def delete_index_files():
    """
    Used by Clear Repo button.
    """

    global metadata, cache

    index.reset()

    metadata.clear()

    cache.clear()

    if os.path.exists(FAISS_PATH):
        os.remove(FAISS_PATH)

    if os.path.exists(META_PATH):
        os.remove(META_PATH)

    print("🗑️ Vector database deleted")


def store_chunks(
    chunks,
    embed_fn
):

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

    print(
        f"✅ Added {added} chunks"
    )

    print(
        f"📊 Total vectors: {index.ntotal}"
    )


load_state()
