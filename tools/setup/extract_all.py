"""Extract PDFs in Material/ to sibling .md + .pages/*.png using Docling.

Idempotent: skips a PDF if its sibling .md already exists, unless --force.
Writes per-page markdown with `## Page N` headers and per-page PNGs at ~200dpi.
Flags pages with empty text or high visual content.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


IMAGES_SCALE = 2.78  # ~200dpi at 72dpi base
VISUAL_TEXT_THRESHOLD = 200  # chars; below this + has images -> visual marker


def build_converter() -> DocumentConverter:
    opts = PdfPipelineOptions()
    opts.generate_page_images = True
    opts.images_scale = IMAGES_SCALE
    opts.do_formula_enrichment = False
    opts.do_table_structure = True
    opts.do_ocr = False
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )


def find_pdfs(target: Path) -> list[Path]:
    if target.is_file() and target.suffix.lower() == ".pdf":
        return [target]
    return sorted(target.rglob("*.pdf"))


def page_has_images(doc, page_no: int) -> bool:
    for item, _ in doc.iterate_items():
        if not getattr(item, "prov", None):
            continue
        if item.prov[0].page_no != page_no:
            continue
        label = getattr(item, "label", None)
        if label and str(label).lower().endswith("picture"):
            return True
    return False


def extract_pdf(pdf_path: Path, converter: DocumentConverter) -> tuple[int, int, int]:
    """Extract one PDF. Returns (pages, visual_flagged, empty_flagged)."""
    md_path = pdf_path.with_suffix(".md")
    pages_dir = pdf_path.with_suffix("").with_name(pdf_path.stem + ".pages")

    result = converter.convert(str(pdf_path))
    doc = result.document

    pages_dir.mkdir(exist_ok=True)

    md_lines: list[str] = [f"# {pdf_path.stem}", ""]
    visual_flagged = 0
    empty_flagged = 0
    total_pages = 0

    for page_no in sorted(doc.pages.keys()):
        total_pages += 1
        page_md = doc.export_to_markdown(page_no=page_no).strip()
        text_len = len(page_md)

        markers: list[str] = []
        if text_len == 0:
            markers.append("*[empty text — see .pages/p{:03d}.png]*".format(page_no))
            empty_flagged += 1
        elif text_len < VISUAL_TEXT_THRESHOLD and page_has_images(doc, page_no):
            markers.append(
                "*[high visual content — prefer .pages/p{:03d}.png]*".format(page_no)
            )
            visual_flagged += 1

        md_lines.append(f"## Page {page_no}")
        md_lines.append("")
        if markers:
            md_lines.extend(markers)
            md_lines.append("")
        if page_md:
            md_lines.append(page_md)
            md_lines.append("")

        page = doc.pages[page_no]
        page_image = getattr(page, "image", None)
        pil = getattr(page_image, "pil_image", None) if page_image else None
        if pil is not None:
            pil.save(pages_dir / f"p{page_no:03d}.png")

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return total_pages, visual_flagged, empty_flagged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="PDF file or directory to walk")
    parser.add_argument("--force", action="store_true", help="Re-extract even if .md exists")
    args = parser.parse_args()

    pdfs = find_pdfs(args.target)
    if not pdfs:
        print(f"No PDFs found under {args.target}", file=sys.stderr)
        return 1

    converter = build_converter()

    grand_pages = grand_visual = grand_empty = 0
    skipped = 0
    failed: list[tuple[Path, str]] = []

    for pdf in pdfs:
        md_path = pdf.with_suffix(".md")
        if md_path.exists() and not args.force:
            print(f"SKIP  {pdf.relative_to(args.target.parent if args.target.is_file() else args.target.parent)}  (.md exists)")
            skipped += 1
            continue
        try:
            pages, visual, empty = extract_pdf(pdf, converter)
        except Exception as e:
            failed.append((pdf, str(e)))
            print(f"FAIL  {pdf.name}: {e}")
            continue
        grand_pages += pages
        grand_visual += visual
        grand_empty += empty
        print(
            f"OK    {pdf.name}: {pages} pages, "
            f"{visual + empty} flagged ({visual} visual, {empty} empty)"
        )

    print()
    print(
        f"TOTAL: {grand_pages} pages across {len(pdfs) - skipped - len(failed)} PDFs, "
        f"{grand_visual + grand_empty} flagged ({grand_visual} visual, {grand_empty} empty)"
    )
    if skipped:
        print(f"SKIPPED: {skipped} (sibling .md already exists; use --force to redo)")
    if failed:
        print(f"FAILED: {len(failed)}")
        for pdf, err in failed:
            print(f"  - {pdf}: {err}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
