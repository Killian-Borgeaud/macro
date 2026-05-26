"""Slice Material/textbook.pdf into per-chapter PDFs placed directly in their
target module folders. Idempotent: skips if target chapter PDF already exists.

Offset: PDF page = book page + 26 (verified for the Sorensen & Whitta-Jacobsen
2nd Edition scan currently at Material/textbook.pdf). If the source PDF
changes, re-verify with the probing script in the report and update RANGES.
"""

from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium


WORKSPACE = Path(__file__).resolve().parents[2]
SOURCE = WORKSPACE / "Material" / "textbook.pdf"
MODULES = WORKSPACE / "Material" / "modules"

# (chapter_number, pdf_start_page, pdf_end_page_inclusive, target_module)
# Pages are 1-indexed (human-readable PDF pages).
RANGES: list[tuple[int, int, int, str]] = [
    (1,  27,  54,  "module 1"),
    (2,  55,  82,  "module 1"),
    (3,  83,  116, "module 1"),
    (4,  117, 152, "module 2"),
    (5,  153, 181, "module 2"),
    (6,  182, 214, "module 3"),
    (7,  215, 240, "module 3"),
    (8,  241, 267, "module 4"),
    (9,  268, 302, "module 4"),
    (10, 303, 327, "module 6"),
    (11, 328, 353, "module 6"),
]


def slice_chapter(src: pdfium.PdfDocument, start: int, end: int, dest: Path) -> int:
    """Copy pages [start, end] (1-indexed inclusive) from src into a new PDF at dest.
    Returns number of pages written."""
    new = pdfium.PdfDocument.new()
    # import_pages expects 0-indexed page indices
    indices = list(range(start - 1, end))
    new.import_pages(src, indices)
    dest.parent.mkdir(parents=True, exist_ok=True)
    new.save(dest)
    return len(indices)


def main() -> int:
    if not SOURCE.exists():
        print(f"Missing source: {SOURCE}")
        return 1

    src = pdfium.PdfDocument(SOURCE)
    total_pages = len(src)
    print(f"Source: {SOURCE.name}  ({total_pages} pages)")
    print()

    grand = 0
    skipped = 0
    written = 0
    for ch, start, end, module in RANGES:
        if end > total_pages:
            print(f"SKIP  ch{ch}: end page {end} > source length {total_pages}")
            continue
        dest = MODULES / module / f"textbook_ch{ch}.pdf"
        if dest.exists():
            print(f"SKIP  ch{ch} -> {module}/{dest.name}  (already exists)")
            skipped += 1
            continue
        n = slice_chapter(src, start, end, dest)
        print(f"OK    ch{ch} -> {module}/{dest.name}  ({n} pages, PDF {start}-{end})")
        grand += n
        written += 1

    print()
    print(f"TOTAL: {written} chapter PDFs written ({grand} pages), {skipped} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
