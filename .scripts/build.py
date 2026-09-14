import json
import os
import re
import sys
import time

# Allow running from anywhere — resolve sibling notebooks.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notebooks import (
    GITHUB_REPO, LOGO_SVG, LOGO_URL_RAW,
    SECTION_ORDER, SECTION_ICONS,
    discover_notebooks, section_for,
)

# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def banner(title):
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")


def folder_display_name(folder):
    name = re.sub(r"^\d+_", "", folder)
    name = name.replace("_", " ")
    name = name.replace("Variables Data Types", "Variables & Data Types")
    return name


# ══════════════════════════════════════════════════════════════════════════════
# Step 1 — Navigation
# ══════════════════════════════════════════════════════════════════════════════

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

    # Strip any existing nav cells
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


def build_navigation(base_dir, notebooks):
    banner("Step 1 — Adding navigation to notebooks")
    ok = skip = init = 0
    for i in range(len(notebooks)):
        path, _ = notebooks[i]
        full_path = os.path.join(base_dir, path)
        if not os.path.exists(full_path):
            skip += 1
        elif os.path.getsize(full_path) == 0:
            init += 1
        else:
            ok += 1
        process_notebook(i, notebooks, base_dir)
    print(f"\n  ✓ {ok} updated  |  {init} initialised  |  {skip} skipped")


# ══════════════════════════════════════════════════════════════════════════════
# Step 2 — README
# ══════════════════════════════════════════════════════════════════════════════

BADGE_COLOR = "FFD43B&labelColor=3776AB"


def shields_badge(label, message, url, color=BADGE_COLOR):
    img = f"https://img.shields.io/badge/{label}-{message}-{color}?style=flat"
    return f'<a href="{url}"><img src="{img}" alt="{label}"></a>'


def build_readme(base_dir, notebooks):
    banner("Step 2 — Generating README.md")

    # Group notebooks by folder
    folders = {}
    for path, title in notebooks:
        folder = path.split(os.sep)[0]
        folders.setdefault(folder, []).append((path, title))

    # Group folders by section, preserving SECTION_ORDER
    sections = {s: [] for s in SECTION_ORDER}
    sections["Other"] = []
    for folder in folders:
        section = section_for(folder)
        sections.setdefault(section, []).append(folder)

    lines = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines += [
        '<div align="center">',
        f'  <a href="{GITHUB_REPO}">',
        f'    <img src="{LOGO_SVG}" alt="Learn Python" width="480">',
        '  </a>',
        '  <br><br>',
        '  <p>A step-by-step guide to learn Python programming from basics to advanced topics.</p>',
        '',
        '  ' + shields_badge("Stars", "★",    f"{GITHUB_REPO}/stargazers"),
        '  ' + shields_badge("Forks", "fork",  f"{GITHUB_REPO}/network/members"),
        '  ' + shields_badge("License", "MIT", f"{GITHUB_REPO}/blob/main/LICENSE"),
        '  ' + shields_badge("Python", "3.11+", "https://www.python.org/downloads/", "3776AB&labelColor=FFD43B"),
        '</div>',
        '',
        '---',
        '',
        '## Table of Contents',
        '',
    ]

    # ── TOC: section → folder → notebooks ─────────────────────────────────────
    global_index = 1
    for section in SECTION_ORDER + ["Other"]:
        section_folders = sections.get(section, [])
        if not section_folders:
            continue

        icon = SECTION_ICONS.get(section, "📄")
        lines.append(f"### {icon} {section}")
        lines.append("")

        for folder in section_folders:
            folder_name = folder_display_name(folder)
            entries = folders[folder]

            if len(entries) == 1:
                path, title = entries[0]
                link_path = path.replace(" ", "%20").replace("\\", "/")
                lines.append(f"**{global_index:02d}.** 📄 [{folder_name}]({link_path})")
                lines.append("")
                global_index += 1
            else:
                lines.append(f"**{global_index:02d}.** 📁 **{folder_name}**")
                lines.append("")
                global_index += 1
                for path, title in entries:
                    link_path = path.replace(" ", "%20").replace("\\", "/")
                    lines.append(f"&nbsp;&nbsp;&nbsp;&nbsp;↳ [{title}]({link_path})")
                lines.append("")

    # ── Getting Started ────────────────────────────────────────────────────────
    lines += [
        "---",
        "",
        "## 🐍 Getting Started",
        "",
        "1. **Clone the repository**",
        "   ```bash",
        f"   git clone {GITHUB_REPO}.git",
        "   cd learn-python",
        "   ```",
        "",
        "2. **Install Jupyter Notebook**",
        "   ```bash",
        "   pip install jupyter",
        "   ```",
        "",
        "3. **Launch Jupyter**",
        "   ```bash",
        "   jupyter notebook",
        "   ```",
        "",
        "4. **Start learning** — open any notebook from the table above and follow along.",
        "",
        "---",
        "",
        "## 🤝 Contributing",
        "",
        "Contributions, issues, and feature requests are welcome!  ",
        f"Feel free to open a [pull request]({GITHUB_REPO}/pulls) or [issue]({GITHUB_REPO}/issues).",
        "",
        "---",
        "",
        "## 📄 License",
        "",
        f"This project is open source and available under the [MIT License]({GITHUB_REPO}/blob/main/LICENSE).",
        "",
        "---",
        "",
        '<div align="center">',
        '  Made with ❤️ by <a href="https://github.com/balajidharma">Balaji Dharma</a>',
        "</div>",
        "",
    ]

    readme = "\n".join(lines)
    out_path = os.path.join(base_dir, "README.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"  ✓ Written: {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    start = time.time()

    # Script lives in .scripts/ — one level up is the repo root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'═' * 50}")
    print(f"  Learn Python — Build Script")
    print(f"{'═' * 50}")
    print(f"  Repo root : {base_dir}")

    notebooks = discover_notebooks(base_dir)
    print(f"  Notebooks : {len(notebooks)} found")

    build_navigation(base_dir, notebooks)
    build_readme(base_dir, notebooks)

    elapsed = time.time() - start
    print(f"\n{'═' * 50}")
    print(f"  ✅ Build complete in {elapsed:.2f}s")
    print(f"{'═' * 50}\n")


if __name__ == "__main__":
    main()