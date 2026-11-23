#!/usr/bin/env python3
"""Render executive Excel workbooks (with live formulas), Plotly HTML dashboards, and 300-DPI charts.

Applies corporate styling from `.agents/memory/08_VIZ_STANDARDS.md` and performs
programmatic post-render QA on generated deliverables.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import plotly.graph_objects as go
from jinja2 import Template

PALETTE = ["#1B365D", "#008080", "#D97706", "#15803D", "#475569", "#B91C1C"]
EXCEL_ERROR_TOKENS = {"#DIV/0!", "#REF!", "#VALUE!", "#NAME?", "#N/A", "#NUM!", "#NULL!"}


def load_data(path: Path) -> pd.DataFrame:
    ext = path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext == ".json":
        return pd.read_json(path)
    if ext == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported input format: {ext}")


def render_excel(
    df: pd.DataFrame,
    out_path: Path,
    title: str,
    sheet_name: str,
    sum_cols: list[str],
) -> dict[str, Any]:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name[:31]

    # Title banner
    ws["A1"] = title
    ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="1B365D")
    header_row = 3

    header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    total_font = Font(name="Calibri", size=11, bold=True, color="1B365D")
    thin = Side(border_style="thin", color="CBD5E1")
    double = Side(border_style="double", color="1B365D")
    top_thin = Side(border_style="thin", color="1B365D")

    cols = list(df.columns)
    for col_idx, col_name in enumerate(cols, start=1):
        cell = ws.cell(row=header_row, column=col_idx, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    start_data_row = header_row + 1
    for r_offset, row in enumerate(df.itertuples(index=False)):
        r_num = start_data_row + r_offset
        for c_idx, val in enumerate(row, start=1):
            cell = ws.cell(row=r_num, column=c_idx, value=None if pd.isna(val) else val)
            cell.font = Font(name="Calibri", size=10)
            cell.border = Border(bottom=thin)
            if r_offset % 2 == 1:
                cell.fill = zebra_fill
            if isinstance(val, float):
                cell.number_format = "#,##0.00"
            elif isinstance(val, int) and not isinstance(val, bool):
                cell.number_format = "#,##0"

    end_data_row = start_data_row + len(df) - 1
    total_row = end_data_row + 1
    if len(df) > 0:
        ws.cell(row=total_row, column=1, value="Total").font = total_font
        for c_idx, col_name in enumerate(cols, start=1):
            cell = ws.cell(row=total_row, column=c_idx)
            cell.font = total_font
            cell.border = Border(top=top_thin, bottom=double)
            if col_name in sum_cols or (not sum_cols and pd.api.types.is_numeric_dtype(df[col_name])):
                col_letter = get_column_letter(c_idx)
                cell.value = f"=SUM({col_letter}{start_data_row}:{col_letter}{end_data_row})"
                cell.number_format = "#,##0.00" if pd.api.types.is_float_dtype(df[col_name]) else "#,##0"

    # Freeze panes, auto-filter, and auto-fit columns
    ws.freeze_panes = f"A{start_data_row}"
    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(len(cols))}{end_data_row}"
    for c_idx, col_name in enumerate(cols, start=1):
        max_len = max([len(str(col_name))] + [len(str(v)) for v in df[col_name].head(200).tolist()])
        ws.column_dimensions[get_column_letter(c_idx)].width = min(max(max_len + 4, 12), 45)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)
    wb.close()

    # Post-render QA: re-open and verify formulas & zero error tokens
    qa_wb = openpyxl.load_workbook(out_path, data_only=False)
    qa_ws = qa_wb[ws.title]
    formula_count = 0
    error_cells: list[str] = []
    for row in qa_ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                if cell.value.startswith("="):
                    formula_count += 1
                elif cell.value.strip() in EXCEL_ERROR_TOKENS:
                    error_cells.append(cell.coordinate)
    qa_wb.close()
    return {
        "mode": "excel",
        "output": str(out_path),
        "rows_written": len(df),
        "formula_cells_verified": formula_count,
        "error_cells": error_cells,
        "qa_status": "PASS" if not error_cells else "FAIL",
    }


HTML_TEMPLATE = Template(
    """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{{ title }}</title>
<style>
  body { font-family: Inter, 'Segoe UI', Arial, sans-serif; margin: 0; padding: 24px; background: #F8FAFC; color: #0F172A; }
  h1 { color: #1B365D; margin-bottom: 4px; }
  .subtitle { color: #475569; margin-bottom: 20px; font-size: 14px; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 24px; }
  .card { background: #FFFFFF; border-left: 4px solid #1B365D; border-radius: 6px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .card-label { font-size: 12px; text-transform: uppercase; color: #475569; letter-spacing: 0.04em; }
  .card-value { font-size: 22px; font-weight: 700; color: #1B365D; margin-top: 6px; font-variant-numeric: tabular-nums; }
  .panel { background: #FFFFFF; border-radius: 8px; padding: 18px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  table { width: 100%; border-collapse: collapse; font-size: 13px; font-variant-numeric: tabular-nums; }
  th { background: #1B365D; color: #FFFFFF; text-align: left; padding: 8px 10px; }
  td { padding: 7px 10px; border-bottom: 1px solid #E2E8F0; }
  tr:nth-child(even) td { background: #F8FAFC; }
</style>
</head>
<body>
  <h1>{{ title }}</h1>
  <div class="subtitle">{{ subtitle }}</div>
  <div class="cards">
    {% for k in kpis %}
    <div class="card">
      <div class="card-label">{{ k.label }}</div>
      <div class="card-value">{{ k.value }}</div>
    </div>
    {% endfor %}
  </div>
  {% if chart_html %}
  <div class="panel">{{ chart_html | safe }}</div>
  {% endif %}
  <div class="panel">
    {{ table_html | safe }}
  </div>
</body>
</html>"""
)


def render_html(
    df: pd.DataFrame,
    out_path: Path,
    title: str,
    subtitle: str,
    x_col: str | None,
    y_cols: list[str],
) -> dict[str, Any]:
    numeric_cols = y_cols or [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])][:4]
    kpis = [{"label": c, "value": f"{df[c].sum():,.2f}"} for c in numeric_cols if c in df.columns]

    chart_html = ""
    if x_col and x_col in df.columns and numeric_cols:
        fig = go.Figure()
        for idx, yc in enumerate(numeric_cols):
            if yc in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df[x_col],
                        y=df[yc],
                        mode="lines+markers",
                        name=yc,
                        line=dict(color=PALETTE[idx % len(PALETTE)], width=2.5),
                    )
                )
        fig.update_layout(
            template="plotly_white",
            title=title,
            xaxis_title=x_col,
            yaxis=dict(rangemode="tozero", gridcolor="#E2E8F0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=20, t=55, b=40),
        )
        chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

    table_html = df.head(500).to_html(index=False, border=0, classes="data-table")
    html = HTML_TEMPLATE.render(
        title=title,
        subtitle=subtitle or f"Rows: {len(df):,}",
        kpis=kpis,
        chart_html=chart_html,
        table_html=table_html,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return {
        "mode": "html",
        "output": str(out_path),
        "bytes": out_path.stat().st_size,
        "qa_status": "PASS" if out_path.stat().st_size > 200 else "FAIL",
    }


def render_chart(
    df: pd.DataFrame,
    out_path: Path,
    title: str,
    subtitle: str,
    x_col: str,
    y_cols: list[str],
    kind: str,
) -> dict[str, Any]:
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    for idx, yc in enumerate(y_cols):
        color = PALETTE[idx % len(PALETTE)]
        if kind == "bar":
            ax.bar(df[x_col].astype(str), df[yc], label=yc, color=color, alpha=0.9)
        else:
            ax.plot(df[x_col].astype(str), df[yc], marker="o", linewidth=2.2, label=yc, color=color)

    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color="#1B365D", pad=18)
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=10, color="#475569")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, color="#CBD5E1")
    ax.set_axisbelow(True)
    if kind == "bar":
        ax.set_ylim(bottom=0)
    if len(y_cols) > 1:
        ax.legend(frameon=False)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return {
        "mode": "chart",
        "output": str(out_path),
        "bytes": out_path.stat().st_size,
        "qa_status": "PASS" if out_path.stat().st_size > 0 else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render executive Excel, HTML, or high-DPI chart deliverables.")
    parser.add_argument("--mode", choices=["excel", "html", "chart"], required=True)
    parser.add_argument("--input", required=True, help="Validated input dataset (.csv/.json/.parquet).")
    parser.add_argument("--output", required=True, help="Target output file path in output/.")
    parser.add_argument("--title", default="Executive Report", help="Report or chart title.")
    parser.add_argument("--subtitle", default="", help="Subtitle with date range / units.")
    parser.add_argument("--sheet-name", default="Report", help="Excel sheet name.")
    parser.add_argument("--sum-cols", default="", help="Comma-separated columns to SUM in Excel total row.")
    parser.add_argument("--x-col", default=None, help="X-axis column for charts/dashboards.")
    parser.add_argument("--y-cols", default="", help="Comma-separated Y-axis columns.")
    parser.add_argument("--chart-kind", choices=["line", "bar"], default="line")
    args = parser.parse_args()

    df = load_data(Path(args.input))
    out_path = Path(args.output)
    sum_cols = [c.strip() for c in args.sum_cols.split(",") if c.strip()]
    y_cols = [c.strip() for c in args.y_cols.split(",") if c.strip()]

    if args.mode == "excel":
        report = render_excel(df, out_path, args.title, args.sheet_name, sum_cols)
    elif args.mode == "html":
        report = render_html(df, out_path, args.title, args.subtitle, args.x_col, y_cols)
    else:
        if not args.x_col or not y_cols:
            parser.error("--x-col and --y-cols are required for --mode chart")
        report = render_chart(df, out_path, args.title, args.subtitle, args.x_col, y_cols, args.chart_kind)

    print(json.dumps(report, indent=2))
    return 0 if report.get("qa_status") == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
