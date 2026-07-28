# Agent Instructions

<!-- BEGIN NOTES-SITE-MACHINERY -->

## Notes Site Machinery

Apply this section only when the notes-site machinery is present in this repo.
As a quick check, look for `build_site.py`, `site.yml`, and a `justfile` with
recipes such as `quick`, `latex`, and `site`. If those files/recipes are absent,
ignore this managed block and follow the rest of the repo's agent instructions.

This repo uses the org-project-template machinery to build a static website from
mixed Org and LaTeX notes, and to collect coherent LaTeX output from those same
notes.

### Source And Generated Paths

- Source notes live under `notes/`.
- Org notes (`.org`) are exported by `export-fragments.el`.
- LaTeX notes (`.tex`) are exported by `export_tex.py` through pandoc.
- Intermediate HTML fragments go under `build/`.
- Final site output goes under `public/`.
- Collected LaTeX output goes under `build/latex/`.
- Treat `build/` and `public/` as generated output. Do not hand-edit them.

### Python And Commands

- Use `uv` for Python commands and dependency isolation.
- Prefer `uv run python ...` over plain `python ...` when running repository
  Python scripts manually.
- If the repo has no `pyproject.toml` or lockfile, use transient uv
  dependencies when needed, for example
  `uv run --with pyyaml python build_site.py`.
- Use the `justfile` interface for normal workflows:
  `just quick`, `just latex`, `just build`, `just site`, `just serve`, and
  `just clean`.
- Do not introduce Node, React, Django, or another frontend/build framework.

### Build Contract

The path contract is mirrored:

```text
notes/foo.org      -> build/foo.html      -> public/foo.html
notes/bar.tex      -> build/bar.html      -> public/bar.html
notes/sub/baz.org  -> build/sub/baz.html  -> public/sub/baz.html
```

The builder is format-agnostic after fragment export. Preserve this split:
Emacs exports Org, pandoc exports LaTeX, and `build_site.py` wraps fragments,
builds navigation/index pages, copies assets, and validates local links.

### Note Metadata

Every rendered note needs `TITLE` metadata.

Org notes:

```org
#+TITLE: A note title
#+DESCRIPTION: Optional index-card summary
```

LaTeX notes, before `\documentclass`:

```latex
%+TITLE: A note title
%+DESCRIPTION: Optional index-card summary
\documentclass{article}
```

Do not create both `notes/foo.org` and `notes/foo.tex`; they both map to
`foo.html` and the builder should reject that clash.

### LaTeX Notes

- Shared macros belong in `site/latex/macros.tex` and should be included from
  notes with `\input`.
- Shared preamble/package setup belongs in `site/latex/header.tex`.
- Plain `\newcommand` macros are expanded by pandoc during HTML conversion, so
  MathJax should not need duplicate macro definitions.
- For direct PDF builds of hand-written `.tex` notes, compile from the note's
  directory so relative `\input` and figure paths resolve naturally.

### Menus, Sections, And Assets

- Menu grouping and order are controlled in `site.yml`, not note metadata.
- `notes.order` is a global list of note slugs. A slug is the note path under
  `notes/` without `.org` or `.tex`.
- `notes.sections` lists subfolders rendered as submenus.
- Only listed section subfolders are scanned recursively for notes.
- Other note subfolders, such as `notes/figures/`, are assets and should not be
  rendered as pages.
- Asset copy rules live in `site.yml`. Fix broken links or asset mappings
  instead of disabling local link validation.

### Org Export

- Org export uses `emacsclient` when `.org` notes exist.
- If the repo contains Org notes, ensure an Emacs server is running before
  relying on `just quick`, `just site`, or `just latex`.
- Org source blocks should not execute during rendering unless explicitly
  requested.
- Org transclusions use whole-file links only, for example
  `#+transclude: [[file:shared/preamble.org]]`.

### Verification

Before handing off changes that touch notes, templates, assets, exporters, or
builder logic, run:

```sh
uv run --with pyyaml python -m py_compile build_site.py export_tex.py serve_site.py
just quick
```

For changes that affect collected LaTeX output, also run:

```sh
just latex
```

If verification cannot run because `uv`, `pandoc`, `just`, or an Emacs server
is missing, report that explicitly.

### Editing Boundaries

- Edit source files such as `notes/`, `site/`, `site.yml`, `build_site.py`,
  `export_tex.py`, `export-fragments.el`, `serve_site.py`, `justfile`, and
  documentation.
- Avoid editing generated files under `build/` or `public/`.
- Keep templates plain HTML with simple `{{ placeholder }}` replacement.
- Keep CSS and JavaScript framework-free.
- Keep local link validation active.

<!-- END NOTES-SITE-MACHINERY -->
