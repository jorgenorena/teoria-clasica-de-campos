#!/usr/bin/env python3
"""Export hand-written LaTeX notes for the static site.

Two responsibilities, mirroring the Org toolchain:

    fragments   notes/**/*.tex -> build/**/*.html        (via pandoc, body-only)
    latex       notes/**/*.tex -> build/latex/**/*.tex    (verbatim copy)

The HTML fragments are body-only and land in the same place the Org exporter
writes to, so ``build_site.py`` wraps them into pages without caring whether a
note came from Org or LaTeX.

Conversion notes:

- Math is left as raw TeX for MathJax (``--mathjax``).
- ``\\newcommand`` macros are expanded by pandoc, so MathJax never needs them.
- Headings are shifted down one level (``--shift-heading-level-by=1``) so
  ``\\section`` becomes ``<h2>``, matching Org notes and the section nav.
- ``\\begin{info}...\\end{info}`` becomes ``<div class="info">`` automatically.
- pandoc runs with the note's own directory as the working directory, so
  ``\\input`` and ``\\includegraphics`` resolve the way pdflatex would when the
  note is compiled in place.
"""
from __future__ import annotations

import hashlib
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "site.yml"

PANDOC_ARGS = [
    "--from=latex",
    "--to=html5",
    "--mathjax",
    "--shift-heading-level-by=1",
]

IMG_SRC_RE = re.compile(
    r"(?P<prefix><img\b[^>]*\bsrc\s*=\s*)(?P<quote>[\"'])(?P<src>.*?)(?P=quote)",
    re.IGNORECASE | re.DOTALL,
)
CONTENT_HASH_LENGTH = 12


def fail(msg: str) -> None:
    raise SystemExit(f"ERROR: {msg}")


def resolve_path(raw: dict, section: str, key: str, default: str) -> Path:
    value = (raw.get(section) or {}).get(key, default)
    if not isinstance(value, str) or not value:
        fail(f"site.yml field {section}.{key} must be a non-empty path string")
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def load_sections(raw: dict, notes_dir: Path) -> list[str]:
    """Return the subfolders ``notes.menu`` scans (mirrors build_site.py).

    Only the folder names matter here, not the order, so this resolves bare
    entries the same way: a bare entry is a subfolder when no note of that name
    exists. Any subfolder the menu never reaches is treated as assets and
    skipped, so its .tex files are never converted.
    """
    notes = raw.get("notes") or {}
    if notes.get("sections") is not None or notes.get("order") is not None:
        fail(
            "site.yml fields notes.sections / notes.order have been replaced "
            "by notes.menu; see the README section 'The Menu'."
        )

    items = notes.get("menu", [])
    if items is None:
        return []
    if not isinstance(items, list):
        fail("site.yml field notes.menu must be a list")

    names: list[str] = []
    for i, item in enumerate(items, start=1):
        if isinstance(item, str):
            name = item.strip()
            if not name:
                fail(f"site.yml notes.menu[{i}] must be a non-empty string")
            # A bare entry naming a real note is a note, not a folder.
            if any((notes_dir / f"{name}{ext}").is_file() for ext in (".org", ".tex")):
                continue
        elif isinstance(item, dict):
            name = item.get("dir")
            if not isinstance(name, str) or not name.strip():
                fail(f"site.yml notes.menu[{i}].dir must be a non-empty string")
            name = name.strip()
        else:
            fail(f"site.yml notes.menu[{i}] must be a string or a mapping")
        names.append(name)
    return names


def load_paths() -> tuple[Path, Path, Path, list[str]]:
    if not CONFIG_PATH.exists():
        fail(f"missing site configuration: {CONFIG_PATH}")
    raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        fail(f"{CONFIG_PATH} must contain a YAML mapping")

    notes_dir = resolve_path(raw, "notes", "root", "notes")
    fragments_dir = resolve_path(raw, "fragments", "root", "build")
    latex_dir = resolve_path(raw, "latex", "root", "build/latex")
    sections = load_sections(raw, notes_dir)
    return notes_dir, fragments_dir, latex_dir, sections


def tex_notes(notes_dir: Path, sections: list[str]) -> list[Path]:
    """Discover .tex notes the same way build_site.py does: top-level notes
    plus each subfolder reached by notes.menu (recursively). Unlisted
    subfolders are left alone so asset .tex files are never converted."""
    if not notes_dir.is_dir():
        fail(f"notes directory does not exist: {notes_dir}")

    found = list(notes_dir.glob("*.tex"))
    for name in sections:
        section_dir = notes_dir / name
        if section_dir.is_dir():
            found.extend(section_dir.rglob("*.tex"))
    return sorted(set(found))


def add_image_content_hashes(fragment: str, source_dir: Path) -> str:
    """Append a content hash to local image URLs in a Pandoc fragment."""

    def replace(match: re.Match[str]) -> str:
        raw_src = match.group("src")
        decoded_src = html.unescape(raw_src)
        split = urlsplit(decoded_src)

        if split.scheme or split.netloc or not split.path or split.path.startswith("/"):
            return match.group(0)

        image_path = source_dir / unquote(split.path)
        if not image_path.is_file():
            return match.group(0)

        digest = hashlib.sha256(image_path.read_bytes()).hexdigest()[:CONTENT_HASH_LENGTH]
        separator = "&amp;" if split.query else "?"
        src_without_fragment, marker, raw_fragment = raw_src.partition("#")
        fragment_suffix = f"{marker}{raw_fragment}"
        hashed_src = f"{src_without_fragment}{separator}v={digest}{fragment_suffix}"
        return (
            f'{match.group("prefix")}{match.group("quote")}'
            f'{hashed_src}{match.group("quote")}'
        )

    return IMG_SRC_RE.sub(replace, fragment)


def export_fragment(note: Path, notes_dir: Path, fragments_dir: Path) -> None:
    out_file = fragments_dir / note.relative_to(notes_dir).with_suffix(".html")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    print(f"pandoc {note} -> {out_file}")

    result = subprocess.run(
        ["pandoc", note.name, *PANDOC_ARGS, "-o", str(out_file)],
        cwd=note.parent,
        capture_output=True,
        text=True,
    )
    if result.stderr.strip():
        sys.stderr.write(result.stderr)
    if result.returncode != 0:
        fail(f"pandoc failed on {note} (exit {result.returncode})")

    fragment = out_file.read_text(encoding="utf-8")
    out_file.write_text(
        add_image_content_hashes(fragment, note.parent),
        encoding="utf-8",
    )


def copy_latex(note: Path, notes_dir: Path, latex_dir: Path) -> None:
    out_file = latex_dir / note.relative_to(notes_dir)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    print(f"copy {note} -> {out_file}")
    shutil.copy2(note, out_file)


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "fragments"
    if mode not in {"fragments", "latex"}:
        fail(f"unknown mode: {mode!r} (expected 'fragments' or 'latex')")

    notes_dir, fragments_dir, latex_dir, sections = load_paths()
    notes = tex_notes(notes_dir, sections)

    if not notes:
        print(f"No .tex notes found in {notes_dir}; nothing to do.")
        return

    if mode == "fragments":
        if shutil.which("pandoc") is None:
            fail("pandoc not found on PATH; install pandoc to export LaTeX notes")
        for note in notes:
            export_fragment(note, notes_dir, fragments_dir)
        print(f"Exported {len(notes)} LaTeX note(s) to HTML fragments.")
    else:
        for note in notes:
            copy_latex(note, notes_dir, latex_dir)
        print(f"Copied {len(notes)} LaTeX note(s) into {latex_dir}.")


if __name__ == "__main__":
    main()
