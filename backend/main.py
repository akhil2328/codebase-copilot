import os
import subprocess

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from repo_loader import get_last_repo

from pipeline import build_index, answer

import vector_store

from vector_store import (
    metadata,
    delete_index_files
)
from repo_loader import delete_repo

app = FastAPI()

BASE_REPO_PATH = os.path.abspath("data/repo")


# --------------------------------------------------
# FILE TREE
# --------------------------------------------------

def build_tree(path):

    if not os.path.exists(path):
        return []

    tree = []

    for item in os.listdir(path):

        full = os.path.join(path, item)

        if os.path.isdir(full):

            tree.append({
                "name": item,
                "type": "folder",
                "children": build_tree(full)
            })

        else:

            tree.append({
                "name": item,
                "type": "file",
                "path": full.replace("\\", "/")
            })

    return tree


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# INDEX REPOSITORY
# --------------------------------------------------

@app.post("/index")
def index_repo(url: str = Query(...)):

    build_index(url)

    return {
        "status": "indexed",
        "vectors": vector_store.index.ntotal
    }


# --------------------------------------------------
# ASK QUESTION
# --------------------------------------------------

@app.get("/ask")
def ask(q: str = Query(...)):

    result = answer(q)

    return {
        "answer": result
    }


# --------------------------------------------------
# STREAM ANSWER
# --------------------------------------------------

@app.get("/ask-stream")
def ask_stream(q: str = Query(...)):

    def generate():

        text = answer(q)

        for ch in text:
            yield ch

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )


# --------------------------------------------------
# CLEAR REPOSITORY
# --------------------------------------------------

@app.delete("/clear")
def clear_repository():

    import pipeline

    delete_repo()

    delete_index_files()

    pipeline.history.clear()

    pipeline.index_built = False

    return {
        "status": "cleared",
        "message": "Repository and vector database removed"
    }


# --------------------------------------------------
# FILE EXPLORER
# --------------------------------------------------

@app.get("/files")
def list_files():

    return build_tree(BASE_REPO_PATH)


# --------------------------------------------------
# READ FILE
# --------------------------------------------------

@app.get("/file")
def read_file(path: str):

    full = os.path.abspath(path)

    if not full.startswith(BASE_REPO_PATH):
        raise HTTPException(
            status_code=400,
            detail="Invalid path"
        )

    if not os.path.exists(full):
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    with open(
        full,
        "r",
        encoding="utf8",
        errors="ignore"
    ) as f:

        return {
            "content": f.read()
        }


# --------------------------------------------------
# STATUS
# --------------------------------------------------

@app.get("/status")
def status():

    import pipeline

    return {
        "indexed": pipeline.index_built,
        "vectors": vector_store.index.ntotal
    }


# --------------------------------------------------
# DEBUG
# --------------------------------------------------

@app.get("/debug")
def debug():

    return {
        "chunks": len(vector_store.metadata),
        "vectors": vector_store.index.ntotal
    }


# --------------------------------------------------
# GIT DIFF
# --------------------------------------------------

@app.get("/diff")
def get_diff(
    a: str = Query(...),
    b: str = Query(...)
):

    repo = os.path.abspath("data/repo")

    if not os.path.exists(repo):

        raise HTTPException(
            status_code=404,
            detail="Repository not indexed"
        )

    out = subprocess.check_output(
        ["git", "diff", a, b],
        cwd=repo
    )

    return {
        "diff": out.decode(
            "utf8",
            "ignore"
        )
    }


@app.get("/last-repo")
def last_repo():

    return {
        "url": get_last_repo()
    }
