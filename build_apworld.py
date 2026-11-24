"""
Builds the apworld and the release package.

    python build_apworld.py             # dist/bge.apworld
    python build_apworld.py --install   # also copies it to Archipelago's custom_worlds
    python build_apworld.py --release   # also builds dist/beyond-good-and-evil-archipelago-v<version>.zip

The Archipelago folder can be changed with the ARCHIPELAGO_DIR environment variable.
"""
import json
import os
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
APWORLD = os.path.join(DIST, "bge.apworld")
AP_DIR = os.environ.get("ARCHIPELAGO_DIR", r"C:\ProgramData\Archipelago")
RELEASE_FILES = os.path.join(ROOT, "release")   # YAML template and install instructions


def version() -> str:
    with open(os.path.join(ROOT, "bge", "archipelago.json"), encoding="utf-8") as f:
        return json.load(f)["world_version"]


def build_apworld() -> str:
    os.makedirs(DIST, exist_ok=True)
    with zipfile.ZipFile(APWORLD, "w", zipfile.ZIP_DEFLATED) as z:
        for folder, _, files in os.walk(os.path.join(ROOT, "bge")):
            if "__pycache__" in folder:
                continue
            for name in files:
                full = os.path.join(folder, name)
                z.write(full, os.path.relpath(full, ROOT))
    return APWORLD


def build_release() -> str:
    out = os.path.join(DIST, f"beyond-good-and-evil-archipelago-v{version()}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(APWORLD, "bge.apworld")
        for name in sorted(os.listdir(RELEASE_FILES)):
            z.write(os.path.join(RELEASE_FILES, name), name)
    return out


if __name__ == "__main__":
    print(f"Built {build_apworld()}")
    if "--install" in sys.argv:
        target = os.path.join(AP_DIR, "custom_worlds", "bge.apworld")
        shutil.copy2(APWORLD, target)
        print(f"Installed to {target}")
    if "--release" in sys.argv:
        print(f"Built {build_release()}")
