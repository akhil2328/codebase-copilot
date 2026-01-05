import os
import subprocess
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from pipeline import build_index, answer
from vector_store import metadata, index


app = FastAPI()

BASE_REPO_PATH = os.path.abspath("data/repo")


def build_tree(path):
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/index")
def index_repo(url: str = Query(...)):
    build_index(url)
    return {"status": "indexed", "vectors": index.ntotal}


@app.get("/ask")
def ask(q: str = Query(...)):
    result = answer(q)
    return {"answer": result}


@app.get("/ask-stream")
def ask_stream(q: str = Query(...)):

    def generate():
        from pipeline import answer
        text = answer(q)

        for ch in text:
            yield ch

    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/files")
def list_files():
    return build_tree(BASE_REPO_PATH)


@app.get("/file")
def read_file(path: str):
    full = os.path.abspath(path)

    if not full.startswith(BASE_REPO_PATH):
        raise HTTPException(status_code=400, detail="Invalid path")

    with open(full, "r", encoding="utf8", errors="ignore") as f:
        return {"content": f.read()}


@app.get("/status")
def status():
    from pipeline import index_built
    return {"indexed": index_built}


@app.get("/debug")
def debug():
    return {
        "chunks": len(metadata),
        "vectors": index.ntotal
    }


@app.get("/diff")
def get_diff(a: str = Query(...), b: str = Query(...)):
    repo = os.path.abspath("data/repo")
    out = subprocess.check_output(["git", "diff", a, b], cwd=repo)
    return {"diff": out.decode("utf8", "ignore")}
