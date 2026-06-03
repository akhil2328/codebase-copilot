from git import Repo
import shutil
import os
import time

# -----------------------------------
# Paths
# -----------------------------------

TARGET = os.path.abspath("data/repo")
LAST_REPO_FILE = os.path.abspath("data/last_repo.txt")


# -----------------------------------
# Windows delete helpers
# -----------------------------------

def remove_readonly(func, path, _):
    try:
        os.chmod(path, 0o777)
        func(path)
    except Exception:
        pass


def safe_delete(path):

    if not os.path.exists(path):
        return

    for attempt in range(5):
        try:
            shutil.rmtree(path, onerror=remove_readonly)
            return

        except Exception as e:
            print(f"⚠ Delete retry {attempt + 1}: {e}")
            time.sleep(0.5)

    raise RuntimeError("Could not delete existing repo folder")


# -----------------------------------
# Cache helpers
# -----------------------------------

def save_last_repo(url):

    os.makedirs("data", exist_ok=True)

    with open(
        LAST_REPO_FILE,
        "w",
        encoding="utf8"
    ) as f:
        f.write(url)


def get_last_repo():

    if not os.path.exists(LAST_REPO_FILE):
        return None

    try:
        with open(
            LAST_REPO_FILE,
            "r",
            encoding="utf8"
        ) as f:
            return f.read().strip()

    except Exception:
        return None


# -----------------------------------
# Main clone function
# -----------------------------------

def clone_repo(url, target=TARGET):

    target = os.path.abspath(target)

    print(f"📁 Repo path: {target}")

    last_repo = get_last_repo()

    # -----------------------------------
    # Use cached repo if same URL
    # -----------------------------------

    if (
        last_repo == url
        and os.path.exists(target)
    ):
        print("⚡ Using cached repository")
        return target

    # -----------------------------------
    # Fresh clone
    # -----------------------------------

    safe_delete(target)

    os.makedirs(
        os.path.dirname(target),
        exist_ok=True
    )

    print("⬇️ Cloning repo...")

    Repo.clone_from(
        url,
        target,
        depth=1  # faster clone
    )

    save_last_repo(url)

    print("✅ Clone complete")

    return target
