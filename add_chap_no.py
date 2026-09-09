#!/usr/bin/env python3

from pathlib import Path

# The file containing the ordering, one name per line
order_file = Path("order.txt")

pdf_dir = Path("./chap_pdfs")
sub_dir = Path("./submission")

# Read the names, ignoring blank lines and surrounding whitespace
with order_file.open("r", encoding="utf-8") as f:
    files = [line.strip() for line in f if line.strip()]

for chapter_number, name in enumerate(files, start=1):
    old_file = pdf_dir / f"{name}.pdf"
    new_file = sub_dir / f"chap{chapter_number:02d}_{name}.pdf"

    if old_file.exists():
        old_file.rename(new_file)
        print(f"Renamed: {old_file.name} -> {new_file.name}")
    else:
        print(f"WARNING: {old_file.name} not found")

