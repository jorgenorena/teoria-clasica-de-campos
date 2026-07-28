output := `python -c 'import yaml; print(yaml.safe_load(open("site.yml"))["site"]["output"])'`
fragments := `python -c 'import yaml; print(yaml.safe_load(open("site.yml"))["fragments"]["root"])'`
latex_output := `python -c 'import yaml; print(yaml.safe_load(open("site.yml"))["latex"]["root"])'`
notes := `python -c 'import yaml; print(yaml.safe_load(open("site.yml"))["notes"]["root"])'`

default:
    just --list

# Export Org notes to HTML fragments (skips Emacs when there are no .org notes).
fragments:
    #!/usr/bin/env bash
    set -euo pipefail
    # Skip the Emacs export when there are no .org notes; if there ARE .org
    # notes but no reachable daemon, fail loudly rather than half-build.
    org_files="$(find "{{notes}}" -type f -name '*.org' 2>/dev/null || true)"
    if [ -z "$org_files" ]; then
        echo "No .org notes under {{notes}}/; skipping Emacs export."
        exit 0
    fi
    if ! emacsclient --eval t >/dev/null 2>&1; then
        echo "ERROR: found .org notes but could not reach an Emacs daemon." >&2
        echo "Start one with 'emacs --daemon' (or 'M-x server-start' in a running Emacs), then re-run." >&2
        exit 1
    fi
    emacsclient --eval '(progn (load-file "{{justfile_directory()}}/export-fragments.el") (my/site-export-all-fragments))'

tex-fragments:
    python export_tex.py fragments

build:
    python build_site.py

quick: fragments tex-fragments build

# Collect LaTeX for every note (Org exported via Emacs, hand-written .tex copied).
latex:
    #!/usr/bin/env bash
    set -euo pipefail
    # Skip the Emacs step (don't fail) when there are no .org notes, so
    # .tex-only projects still collect their LaTeX in the copy step below.
    org_files="$(find "{{notes}}" -type f -name '*.org' 2>/dev/null || true)"
    if [ -n "$org_files" ]; then
        if ! emacsclient --eval t >/dev/null 2>&1; then
            echo "ERROR: found .org notes but could not reach an Emacs daemon." >&2
            echo "Start one with 'emacs --daemon' (or 'M-x server-start' in a running Emacs), then re-run." >&2
            exit 1
        fi
        emacsclient --eval '(progn (load-file "{{justfile_directory()}}/export-fragments.el") (my/site-export-all-latex))'
    else
        echo "No .org notes under {{notes}}/; skipping Emacs LaTeX export."
    fi
    python export_tex.py latex

serve port="8000":
    python serve_site.py {{ port }}

serve-static port="8000":
    python -m http.server {{ port }} --directory {{ output }}

site port="8000": quick
    python serve_site.py {{ port }}

clean:
    rm -rf {{ fragments }} {{ latex_output }} {{ output }} __pycache__
