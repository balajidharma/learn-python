import os
import re

# ── Config ────────────────────────────────────────────────────────────────────

GITHUB_REPO  = "https://github.com/balajidharma/learn-python"
LOGO_SVG     = "./assets/images/logo.svg"
LOGO_URL_RAW = "https://raw.githubusercontent.com/balajidharma/learn-python/main/assets/images/logo.svg"

# Folders to skip when auto-discovering notebooks
SKIP_DIRS = {".scripts", ".git", "__pycache__", ".ipynb_checkpoints"}

# Map folder prefix → section heading
SECTION_MAP = {
    "01": "Basics",       # Introduction
    "02": "Basics",       # Setup Environment
    "03": "Basics",       # Basic Syntax
    "04": "Basics",       # Variables & Data Types
    "05": "Basics",       # Operators
    "06": "Basics",       # Strings
    "07": "Basics",       # Typecasting
    "08": "Basics",       # Conditionals
    "09": "Basics",       # Loops
    "10": "Basics",       # Functions
    "11": "Intermediate", # Collections
    "12": "Intermediate", # Lists
    "13": "Intermediate", # Tuples
    "14": "Intermediate", # Sets
    "15": "Intermediate", # Dictionaries
    "16": "Intermediate", # Exceptions
    "17": "Intermediate", # User Input
    "18": "Advanced",     # (reserved)
    "19": "Advanced",     # (reserved)
    "20": "Advanced",     # (reserved)
}

# Section display order
SECTION_ORDER = ["Basics", "Intermediate", "Advanced"]

# Section icons for README
SECTION_ICONS = {
    "Basics":       "🐍",
    "Intermediate": "⚙️",
    "Advanced":     "🚀",
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
    stem = os.path.splitext(os.path.basename(path))[0]
    stem = re.sub(r"^\d+_", "", stem)
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