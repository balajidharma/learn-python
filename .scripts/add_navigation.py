import json
import os
import sys

# Allow running from anywhere — resolve sibling notebooks.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notebooks import GITHUB_REPO, LOGO_URL_RAW, discover_notebooks

NAV_IDS = {"nav-top", "nav-bottom"}


def make_nav_cell(index, position, notebooks):
    """Build a nav cell. position is 'top' or 'bottom'."""
    path, _ = notebooks[index]
    nb_dir = os.path.dirname(path)
    parts = []

    if index > 0:
        prev_path, prev_title = notebooks[index - 1]
        prev_rel = os.path.relpath(prev_path, nb_dir).replace("\\", "/")
        parts.append(f"[← Previous: {prev_title}]({prev_rel})")

    parts.append("[🏠 Home](../README.md)")

    if index < len(notebooks) - 1:
        next_path, next_title = notebooks[index + 1]
        next_rel = os.path.relpath(next_path, nb_dir).replace("\\", "/")
        parts.append(f"[Next: {next_title} →]({next_rel})")

    nav_links = " &nbsp;|&nbsp; ".join(parts)

    if position == "top":
        source = (
            f'<div align="center">\n'
            f'  <a href="{GITHUB_REPO}">'
            f'<img src="{LOGO_URL_RAW}" alt="Learn Python" height="60"></a>\n'
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


def process_notebook(index, notebooks, base_dir):
    path, title = notebooks[index]
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

    nav_top    = make_nav_cell(index, "top",    notebooks)
    nav_bottom = make_nav_cell(index, "bottom", notebooks)

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
    # Script lives in .scripts/ — one level up is the repo root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    notebooks = discover_notebooks(base_dir)

    print(f"Repo root: {base_dir}")
    print(f"Found {len(notebooks)} notebooks\n")

    for i in range(len(notebooks)):
        process_notebook(i, notebooks, base_dir)

    print("\nDone! Each notebook now has nav-top and nav-bottom.")


if __name__ == "__main__":
    main()