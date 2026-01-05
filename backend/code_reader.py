import os

BASE = os.path.abspath("data/repo")

# extensions we care about
EXT = (".py", ".js", ".ts", ".java", ".md", ".txt", ".json", ".html", ".css")


def read_code(path=BASE):
    data = []

    if not os.path.exists(path):
        print("❌ Repo path missing:", path)
        return data

    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(EXT):
                full = os.path.join(root, f)
                try:
                    text = open(full, "r", encoding="utf8",
                                errors="ignore").read()
                    data.append({
                        "path": full.replace("\\", "/"),
                        "content": text
                    })
                except Exception as e:
                    print("⚠ Failed reading", full, e)

    print("📄 Files loaded:", len(data))
    return data
