import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notebooks import (
    GITHUB_REPO, LOGO_SVG,
    SECTION_ORDER, SECTION_ICONS,
    discover_notebooks, section_for,
)

BADGE_COLOR = "FFD43B&labelColor=3776AB"

def shields_badge(label, message, url, color=BADGE_COLOR):
    img = f"https://img.shields.io/badge/{label}-{message}-{color}?style=flat"
    return f'<a href="{url}"><img src="{img}" alt="{label}"></a>'


def folder_display_name(folder):
    import re
    name = re.sub(r"^\d+_", "", folder)
    name = name.replace("_", " ")
    name = name.replace("Variables Data Types", "Variables & Data Types")
    return name


def build_readme(base_dir, notebooks):
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
        '  ' + shields_badge("Stars", "★", f"{GITHUB_REPO}/stargazers"),
        '  ' + shields_badge("Forks", "fork", f"{GITHUB_REPO}/network/members"),
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

    return "\n".join(lines)


def main():
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