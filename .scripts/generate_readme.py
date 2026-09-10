import os
import sys

# Allow running from anywhere — resolve sibling notebooks.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notebooks import (
    GITHUB_REPO, LOGO_SVG, SKIP_DIRS,
    discover_notebooks, section_for,
)

# ── README builder ─────────────────────────────────────────────────────────────

BADGE_COLOR = "FFD43B&labelColor=3776AB"

def shields_badge(label, message, url, color=BADGE_COLOR):
    img = f"https://img.shields.io/badge/{label}-{message}-{color}?style=flat"
    return f'<a href="{url}"><img src="{img}" alt="{label}"></a>'


def build_readme(base_dir, notebooks):
    # Group notebooks by section, preserving order
    sections = {}
    for path, title in notebooks:
        folder = path.split(os.sep)[0]
        section = section_for(folder)
        sections.setdefault(section, []).append((path, title))

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
        '  ' + shields_badge("Stars", "★", f"{GITHUB_REPO}/stargazers"),
        '  ' + shields_badge("Forks", "fork", f"{GITHUB_REPO}/network/members"),
        '  ' + shields_badge("License", "MIT", f"{GITHUB_REPO}/blob/main/LICENSE"),
        '</div>',
        '',
        '---',
        '',
        '## Table of Contents',
        '',
    ]

    # ── TOC tables per section ─────────────────────────────────────────────────
    global_index = 1
    for section, entries in sections.items():
        lines.append(f"### {section}")
        lines.append("")
        lines.append("| # | Topic | Notebook |")
        lines.append("|---|-------|----------|")
        for path, title in entries:
            # URL-encode spaces for markdown links
            link_path = path.replace(" ", "%20").replace("\\", "/")
            lines.append(f"| {global_index:02d} | {title} | [{os.path.basename(path)}]({link_path}) |")
            global_index += 1
        lines.append("")

    # ── Getting Started ────────────────────────────────────────────────────────
    lines += [
        "---",
        "",
        "## Getting Started",
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
        "## Contributing",
        "",
        "Contributions, issues, and feature requests are welcome!  ",
        f"Feel free to open a [pull request]({GITHUB_REPO}/pulls) or [issue]({GITHUB_REPO}/issues).",
        "",
        "---",
        "",
        "## License",
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

    return "\n".join(lines)


def main():
    # Script lives in .scripts/ — one level up is the repo root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Repo root: {base_dir}")

    notebooks = discover_notebooks(base_dir)
    print(f"Found {len(notebooks)} notebooks\n")
    for path, title in notebooks:
        print(f"  {path}  →  {title}")

    readme = build_readme(base_dir, notebooks)

    out_path = os.path.join(base_dir, "README.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    main()