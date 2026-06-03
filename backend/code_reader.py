import os

BASE = os.path.abspath("data/repo")

# File types worth indexing
EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".md",
    ".txt",
    ".json",
    ".html",
    ".css",
)

# Folders to ignore
SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    "__pycache__",
    "venv",
    ".venv",
    ".idea",
    ".vscode",
    "coverage",
    "target",
    "out",
    "bin",
    "obj",
}


def read_code(path=BASE):

    files_data = []

    if not os.path.exists(path):
        print("❌ Repo path missing:", path)
        return files_data

    for root, dirs, files in os.walk(path):

        # Skip heavy folders
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:

            if not filename.lower().endswith(EXTENSIONS):
                continue

            full_path = os.path.join(root, filename)

            try:

                with open(
                    full_path,
                    "r",
                    encoding="utf8",
                    errors="ignore"
                ) as f:

                    content = f.read()

                # Skip empty files
                if not content.strip():
                    continue

                files_data.append({
                    "path": full_path.replace("\\", "/"),
                    "content": content
                })

            except Exception as e:
                print(f"⚠ Failed reading {full_path}: {e}")

    print(f"📄 Files loaded: {len(files_data)}")

    return files_data
