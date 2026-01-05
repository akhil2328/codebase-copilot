import re


def chunk_code(files, size=400):

    chunks = []

    func_pattern = re.compile(
        r"(?:def|class)\s+[a-zA-Z0-9_]+\s*\([^)]*\)\s*:?|(?:class)\s+[a-zA-Z0-9_]+\s*:?"
    )

    for f in files:
        text = f["content"]

        matches = list(func_pattern.finditer(text))

        if not matches:
            # fallback to normal chunking
            for i in range(0, len(text), size):
                chunks.append({
                    "path": f["path"],
                    "content": text[i:i+size]
                })
            continue

        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i+1].start() if i+1 < len(matches) else len(text)

            block = text[start:end]

            chunks.append({
                "path": f["path"],
                "content": block
            })

    return chunks
