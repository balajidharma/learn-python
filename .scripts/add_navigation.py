import json
import os

# Ordered list of all notebooks: (relative path from repo root, display title)
NOTEBOOKS = [
    ("01_Introduction/01_Introduction.ipynb", "Introduction"),
    ("02_Setup_Environment/01_Setup_Environment.ipynb", "Setup Environment"),
    ("03_Basic Syntax/01_Basic_Syntax.ipynb", "Basic Syntax"),
    ("04_Variables_Data_Types/01_Variables.ipynb", "Variables"),
    ("04_Variables_Data_Types/02_Data_Types.ipynb", "Data Types"),
    ("05_Operators/01_Operators.ipynb", "Operators"),
    ("05_Operators/02_Arithmetic_Operators.ipynb", "Arithmetic Operators"),
    ("05_Operators/03_Assignment_Operators.ipynb", "Assignment Operators"),
    ("05_Operators/04_Comparison_Operators.ipynb", "Comparison Operators"),
    ("05_Operators/05_Logical_Operators.ipynb", "Logical Operators"),
    ("05_Operators/06_Bitwise_Operators.ipynb", "Bitwise Operators"),
    ("05_Operators/07_Special_Operators.ipynb", "Special Operators"),
    ("06_Strings/01_Strings.ipynb", "Strings"),
    ("07_Typecasting/01_Typecasting.ipynb", "Typecasting"),
    ("09_Loops/01_Loops.ipynb", "Loops"),
    ("10_Functions/01_Functions.ipynb", "Functions"),
    ("11_Collections/01_Collections.ipynb", "Collections"),
    ("12_Lists/01_Lists.ipynb", "Lists"),
    ("13_Tuples/01_Tuples.ipynb", "Tuples"),
    ("14_Sets/01_Sets.ipynb", "Sets"),
    ("15_Dictionaries/01_Dictionaries.ipynb", "Dictionaries"),
    ("17_User_Input/01_User_Input.ipynb", "User Input"),
]

GITHUB_REPO = "https://github.com/balajidharma/learn-python"
LOGO_URL = "https://raw.githubusercontent.com/balajidharma/learn-python/asset/images/logo.svg"

NAV_IDS = {"nav-top", "nav-bottom"}


def make_nav_cell(index, position):
    """Build a nav cell. position is 'top' or 'bottom'."""
    path, _ = NOTEBOOKS[index]
    nb_dir = os.path.dirname(path)
    parts = []

    if index > 0:
        prev_path, prev_title = NOTEBOOKS[index - 1]
        prev_rel = os.path.relpath(prev_path, nb_dir).replace("\\", "/")
        parts.append(f"[← Previous: {prev_title}]({prev_rel})")

    parts.append("[🏠 Home](../README.md)")

    if index < len(NOTEBOOKS) - 1:
        next_path, next_title = NOTEBOOKS[index + 1]
        next_rel = os.path.relpath(next_path, nb_dir).replace("\\", "/")
        parts.append(f"[Next: {next_title} →]({next_rel})")

    nav_links = " &nbsp;|&nbsp; ".join(parts)

    if position == "top":
        source = (
            f'<div align="center">\n'
            f'  <a href="{GITHUB_REPO}">'
            f'<img src="{LOGO_URL}" alt="Learn Python" height="60"></a>\n'
            f'  <br><br>\n'
            f'  <a href="{GITHUB_REPO}">⭐ Star on GitHub</a>'
            f' &nbsp;|&nbsp; '
            f'<a href="{GITHUB_REPO}">📚 Learn Python</a>\n'
            f'</div>\n\n'
            f'---\n'
            f'{nav_links}'
        )
    else:
        source = f"---\n{nav_links}"

    return {
        "cell_type": "markdown",
        "id": f"nav-{position}",
        "metadata": {},
        "source": [source],
    }


def is_nav_cell(cell):
    """Detect previously inserted nav cells by id or content."""
    if cell.get("id") in NAV_IDS:
        return True
    src = "".join(cell.get("source", []))
    return (
        cell.get("cell_type") == "markdown"
        and ("← Previous" in src or "🏠 Home" in src)
        and ("nav" in cell.get("id", "") or src.startswith("---\n") or "balajidharma/learn-python" in src)
    )


def make_stub_nb(title):
    """Return a minimal valid notebook with just a heading cell."""
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "id": "stub-heading",
                "metadata": {},
                "source": [f"# {title}"],
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "3.11.9",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11.9"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def process_notebook(index, base_dir="."):
    path, title = NOTEBOOKS[index]
    full_path = os.path.join(base_dir, path)

    if not os.path.exists(full_path):
        print(f"  SKIP (file not found): {full_path}")
        return

    if os.path.getsize(full_path) == 0:
        print(f"  INIT (empty → stub): {path}")
        nb = make_stub_nb(title)
    else:
        with open(full_path, "r", encoding="utf-8") as f:
            try:
                nb = json.load(f)
            except json.JSONDecodeError as e:
                print(f"  SKIP (invalid JSON): {path} — {e}")
                return

    # Remove any previously added nav cells
    cells = [c for c in nb.get("cells", []) if not is_nav_cell(c)]

    nav_top = make_nav_cell(index, "top")
    nav_bottom = make_nav_cell(index, "bottom")

    # Layout: nav_top → heading → content → nav_bottom
    if cells and cells[0].get("cell_type") == "markdown":
        heading = [cells[0]]
        content = cells[1:]
    else:
        heading = []
        content = cells

    nb["cells"] = [nav_top] + heading + content + [nav_bottom]

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print(f"  OK: {path}")


def main():
    # Script lives in .scripts/ — go one level up to reach the repo root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Repo root: {base_dir}")
    print(f"Processing {len(NOTEBOOKS)} notebooks...\n")

    for i in range(len(NOTEBOOKS)):
        process_notebook(i, base_dir)

    print("\nDone! Each notebook now has a logo + GitHub link at the top and nav links top and bottom.")


if __name__ == "__main__":
    main()