import os
import re

# ── Config ────────────────────────────────────────────────────────────────────

GITHUB_REPO  = "https://github.com/balajidharma/learn-python"
LOGO_SVG     = "./assets/images/logo.svg"
LOGO_URL_RAW = "https://raw.githubusercontent.com/balajidharma/learn-python/assets/images/logo.svg"

# Folders to skip when auto-discovering notebooks
SKIP_DIRS = {".scripts", ".git", "__pycache__", ".ipynb_checkpoints"}

# Map folder prefix → section heading (prefix = leading digits of folder name)
SECTION_MAP = {
    "01": "Getting Started",
    "02": "Getting Started",
    "03": "Core Language",
    "04": "Core Language",
    "05": "Operators",
    "06": "Language Features",
    "07": "Language Features",
    "08": "Language Features",
    "09": "Language Features",
    "10": "Language Features",
    "11": "Collections",
    "12": "Collections",
    "13": "Collections",
    "14": "Collections",
    "15": "Collections",
    "16": "Collections",
    "17": "Language Features",
}

# ── Auto-discovery ─────────────────────────────────────────────────────────────

def folder_prefix(name):
    """Return the leading numeric prefix of a folder name, e.g. '05' from '05_Operators'."""
    m = re.match(r"^(\d+)", name)
    return m.group(1) if m else ""


def notebook_title(path):
    """
    Derive a human-readable title from a notebook filename.
    e.g. '02_Arithmetic_Operators.ipynb' → 'Arithmetic Operators'
    """
    stem = os.path.splitext(os.path.basename(path))[0]   # strip .ipynb
    stem = re.sub(r"^\d+_", "", stem)                     # strip leading number
    return stem.replace("_", " ")


def discover_notebooks(base_dir):
    """
    Walk base_dir, find all .ipynb files, sort by folder then filename,
    and return a list of (relative_path, title) tuples.
    """
    entries = []
    for folder in sorted(os.listdir(base_dir)):
        if folder in SKIP_DIRS or folder.startswith("."):
            continue
        folder_path = os.path.join(base_dir, folder)
        if not os.path.isdir(folder_path):
            continue
        for fname in sorted(os.listdir(folder_path)):
            if not fname.endswith(".ipynb"):
                continue
            rel = os.path.join(folder, fname)
            title = notebook_title(fname)
            entries.append((rel, title))
    return entries


def section_for(folder_name):
    """Return the section heading for a given folder name."""
    prefix = folder_prefix(folder_name)
    return SECTION_MAP.get(prefix, "Other")