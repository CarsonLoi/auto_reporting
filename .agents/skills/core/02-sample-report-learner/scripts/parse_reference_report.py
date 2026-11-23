#!/usr/bin/env python3
"""Deconstruct user-supplied sample reports (.xlsx, .pdf, .csv, .html) for blueprint learning.

Extracts:
  - .xlsx: Sheet names, freeze panes, merged cells, column widths, number formats,
           fonts, fills, live formulas (data_only=False) AND cached values (data_only=True).
  - .pdf:  Page text and structured tables via pdfplumber (with pypdf fallback).
  - .csv:  Headers, inferred dtypes, row count, and sample rows.
  - .html: Structured HTML tables and headings via BeautifulSoup.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import openpyxl
import pandas as pd


def parse_xlsx(path: Path, max_rows: int = 200) -> dict[str, Any]:
    wb_formulas = openpyxl.load_workbook(path, data_only=False)
    wb_values = openpyxl.load_workbook(path, data_only=True)

    result: dict[str, Any] = {"format": "xlsx", "file": str(path), "sheets": {}}
    for name in wb_formulas.sheetnames:
        ws_f = wb_formulas[name]
        ws_v = wb_values[name]

        col_widths = {
            col_letter: round(dim.width, 2)
            for col_letter, dim in ws_f.column_dimensions.items()
            if dim.width is not None
        }
        merged = [str(rng) for rng in ws_f.merged_cells.ranges]

        formulas: list[dict[str, Any]] = []
        style_samples: dict[str, dict[str, Any]] = {}
        rows_data: list[list[Any]] = []

        row_cap = min(ws_f.max_row or 0, max_rows)
        col_cap = ws_f.max_column or 0

        for r in range(1, row_cap + 1):
            row_vals: list[Any] = []
            for c in range(1, col_cap + 1):
                cell_f = ws_f.cell(row=r, column=c)
                cell_v = ws_v.cell(row=r, column=c)
                val_f = cell_f.value
                val_v = cell_v.value
                row_vals.append(val_v)

                if isinstance(val_f, str) and val_f.startswith("="):
                    formulas.append(
                        {
                            "cell": cell_f.coordinate,
                            "formula": val_f,
                            "cached_value": val_v,
                            "number_format": cell_f.number_format,
                        }
                    )

                if r <= 5 and val_f is not None:
                    fill_rgb = None
                    if cell_f.fill and cell_f.fill.fgColor and cell_f.fill.fgColor.type == "rgb":
                        fill_rgb = cell_f.fill.fgColor.rgb
                    font_rgb = None
                    if cell_f.font and cell_f.font.color and cell_f.font.color.type == "rgb":
                        font_rgb = cell_f.font.color.rgb
                    style_samples[cell_f.coordinate] = {
                        "font_name": cell_f.font.name if cell_f.font else None,
                        "font_size": cell_f.font.size if cell_f.font else None,
                        "bold": bool(cell_f.font.bold) if cell_f.font else False,
                        "font_color": font_rgb,
                        "fill_color": fill_rgb,
                        "number_format": cell_f.number_format,
                    }
            rows_data.append(row_vals)

        result["sheets"][name] = {
            "max_row": ws_f.max_row,
            "max_column": ws_f.max_column,
            "freeze_panes": str(ws_f.freeze_panes) if ws_f.freeze_panes else None,
            "merged_cells": merged,
            "column_widths": col_widths,
            "formula_count": len(formulas),
            "formulas": formulas,
            "style_samples_top5_rows": style_samples,
            "cached_values_preview": rows_data,
        }

    wb_formulas.close()
    wb_values.close()
    return result


def parse_pdf(path: Path, max_pages: int = 50) -> dict[str, Any]:
    pages_out: list[dict[str, Any]] = []
    try:
        import pdfplumber

        with pdfplumber.open(path) as pdf:
            for idx, page in enumerate(pdf.pages[:max_pages], start=1):
                pages_out.append(
                    {
                        "page": idx,
                        "text": page.extract_text() or "",
                        "tables": page.extract_tables() or [],
                    }
                )
        extractor = "pdfplumber"
    except Exception:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        for idx, page in enumerate(reader.pages[:max_pages], start=1):
            pages_out.append({"page": idx, "text": page.extract_text() or "", "tables": []})
        extractor = "pypdf"

    return {
        "format": "pdf",
        "file": str(path),
        "extractor": extractor,
        "page_count": len(pages_out),
        "pages": pages_out,
    }


def parse_csv(path: Path, max_rows: int = 50) -> dict[str, Any]:
    df = pd.read_csv(path)
    return {
        "format": "csv",
        "file": str(path),
        "row_count": int(len(df)),
        "columns": [{"name": c, "dtype": str(df[c].dtype)} for c in df.columns],
        "preview_rows": df.head(max_rows).to_dict(orient="records"),
    }


def parse_html(path: Path) -> dict[str, Any]:
    from bs4 import BeautifulSoup

    html_text = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html_text, "lxml")
    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
    tables_out: list[dict[str, Any]] = []
    for idx, tbl in enumerate(soup.find_all("table"), start=1):
        rows = []
        for tr in tbl.find_all("tr"):
            cells = [c.get_text(strip=True) for c in tr.find_all(["th", "td"])]
            if cells:
                rows.append(cells)
        tables_out.append({"table_index": idx, "row_count": len(rows), "rows": rows[:100]})
    return {
        "format": "html",
        "file": str(path),
        "title": soup.title.string.strip() if soup.title and soup.title.string else None,
        "headings": headings,
        "tables": tables_out,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse reference report (.xlsx, .pdf, .csv, .html).")
    parser.add_argument("input_file", help="Path to sample report in references/.")
    parser.add_argument("--out", default=None, help="Optional JSON output file path.")
    parser.add_argument("--max-rows", type=int, default=200, help="Max preview rows per sheet/CSV.")
    args = parser.parse_args()

    path = Path(args.input_file)
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        return 1

    ext = path.suffix.lower()
    if ext in {".xlsx", ".xlsm"}:
        parsed = parse_xlsx(path, max_rows=args.max_rows)
    elif ext == ".pdf":
        parsed = parse_pdf(path)
    elif ext == ".csv":
        parsed = parse_csv(path, max_rows=args.max_rows)
    elif ext in {".html", ".htm"}:
        parsed = parse_html(path)
    else:
        print(f"ERROR: Unsupported file extension '{ext}'. Supported: .xlsx, .pdf, .csv, .html", file=sys.stderr)
        return 1

    rendered = json.dumps(parsed, indent=2, default=str)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
        print(f"Wrote parsed report metadata to {out_path}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
