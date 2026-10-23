#!/usr/bin/env bash
# Prepare a new Superset workspace for building the book.
# There are no package dependencies (python scripts use only the stdlib),
# so this just brings over untracked source material and creates build dirs.
set -euo pipefail

ROOT="${SUPERSET_ROOT_PATH:-}"

# Build output dirs used by the makefile.
mkdir -p tmp chap_pdfs submission

# Copy untracked/ignored source material from the main checkout,
# never overwriting anything already in the workspace.
if [ -n "$ROOT" ] && [ "$ROOT" != "$PWD" ]; then
    for dir in extras word_docs; do
        if [ -d "$ROOT/$dir" ]; then
            rsync -a --ignore-existing "$ROOT/$dir/" "$dir/"
            echo "Copied $dir/"
        fi
    done
    if [ -d "$ROOT/drafts" ]; then
        mkdir -p drafts
        rsync -a --ignore-existing --include='*.docx' --exclude='*' \
            "$ROOT/drafts/" drafts/
        echo "Copied drafts/*.docx"
    fi
else
    echo "SUPERSET_ROOT_PATH not set (or is this checkout); skipping copy."
fi

# Warn (don't fail) about tools the makefile needs.
for tool in pandoc xelatex python3; do
    command -v "$tool" >/dev/null || echo "WARNING: $tool not found on PATH"
done
if [ -z "${INI_HOME:-}" ] || [ ! -f "$INI_HOME/common.mk" ]; then
    echo "WARNING: \$INI_HOME/common.mk not found; make will fail to include it"
fi

echo "Workspace setup complete."
