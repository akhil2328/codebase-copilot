import re

MAX_CHUNK_SIZE = 500


def split_large_block(text, size=MAX_CHUNK_SIZE):

    chunks = []

    for i in range(0, len(text), size):
        chunks.append(text[i:i + size])

    return chunks


def chunk_code(files, size=MAX_CHUNK_SIZE):

    chunks = []

    func_pattern = re.compile(
        r"(?:def|class)\s+[a-zA-Z0-9_]+\s*\([^)]*\)\s*:?|(?:class)\s+[a-zA-Z0-9_]+\s*:?"
    )

    for file in files:

        text = file["content"]

        matches = list(func_pattern.finditer(text))

        # -----------------------------------
        # No functions/classes found
        # -----------------------------------

        if not matches:

            for i in range(0, len(text), size):

                block = text[i:i + size]

                if block.strip():

                    chunks.append({
                        "path": file["path"],
                        "content": block
                    })

            continue

        # -----------------------------------
        # Function / Class chunking
        # -----------------------------------

        for i, match in enumerate(matches):

            start = match.start()

            end = (
                matches[i + 1].start()
                if i + 1 < len(matches)
                else len(text)
            )

            block = text[start:end]

            if not block.strip():
                continue

            # -----------------------------------
            # Split huge functions/classes
            # -----------------------------------

            if len(block) > size:

                pieces = split_large_block(
                    block,
                    size
                )

                for piece in pieces:

                    chunks.append({
                        "path": file["path"],
                        "content": piece
                    })

            else:

                chunks.append({
                    "path": file["path"],
                    "content": block
                })

    print(f"🧩 Chunks created: {len(chunks)}")

    return chunks
