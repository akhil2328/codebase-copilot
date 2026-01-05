from git import Repo
import shutil
import os
import time


TARGET = os.path.abspath("data/repo")


def remove_readonly(func, path, _):
    """Force remove Windows locked files"""
    try:
        os.chmod(path, 0o777)
        func(path)
    except Exception:
        pass


def safe_delete(path):
    """Retry delete a few times to avoid WinError 5"""
    if not os.path.exists(path):
        return

    for attempt in range(5):
        try:
            shutil.rmtree(path, onerror=remove_readonly)
            return
        except Exception as e:
            print(f"⚠ Delete retry {attempt+1}: {e}")
            time.sleep(0.4)

    raise RuntimeError("Could not delete existing repo folder")


def clone_repo(url, target=TARGET):

    target = os.path.abspath(target)

    print(f"📁 Repo path: {target}")

    # delete old one safely
    safe_delete(target)

    print("⬇️ Cloning repo…")
    Repo.clone_from(url, target)

    print("✅ Clone complete")
