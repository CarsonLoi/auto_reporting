#!/usr/bin/env python3
"""Automated 5-Point Validation Gate for Numbers Auditing.

Gates:
  1. ETL Freshness & Completeness Check (optional live DB check or date-column check)
  2. Join Fanout Check (pre_join_rows vs post_join_rows)
  3. Un-Joined Control Total Reconciliation (within +/- tolerance, default 0.01)
  4. Cross-Tab & Ratio-of-Sums Parity (summary vs detail + ratio checks)
  5. Anomaly & Null Integrity Scan (NaN, Inf, Excel error tokens, |z| > 4 outliers)

Exits with code 0 only if all executed gates PASS; exits with code 2 if any gate FAILS.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

EXCEL_ERROR_TOKENS = {"#DIV/0!", "#REF!", "#VALUE!", "#NAME?", "#N/A", "#NUM!", "#NULL!"}


def load_dataset(path: Path) -> pd.DataFrame:
    ext = path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext == ".json":
        return pd.read_json(path)
    if ext == ".parquet":
        return pd.read_parquet(path)
    if ext in {".xlsx", ".xlsm"}:
        return pd.read_excel(path)
    raise ValueError(f"Unsupported dataset format: {ext}")


def gate_1_freshness(
    df: pd.DataFrame,
    date_col: str | None,
    expected_date: str | None,
) -> dict[str, Any]:
    if not date_col or not expected_date:
        return {"status": "SKIPPED", "reason": "No --freshness-date-col / --expected-date provided."}
    if date_col not in df.columns:
        return {"status": "FAIL", "reason": f"Date column '{date_col}' not found in dataset."}

    dates = pd.to_datetime(df[date_col], errors="coerce").dt.strftime("%Y-%m-%d")
    counts = dates.value_counts().sort_index()
    latest_count = int(counts.get(expected_date, 0))
    trailing = counts[counts.index < expected_date].tail(7)
    median_trailing = float(trailing.median()) if len(trailing) > 0 else None

    if latest_count == 0:
        return {
            "status": "FAIL",
            "expected_date": expected_date,
            "latest_row_count": 0,
            "reason": "Latest expected business date has 0 rows (ETL missing/incomplete).",
        }
    warning = None
    if median_trailing and latest_count < 0.5 * median_trailing:
        warning = f"Latest day row count ({latest_count}) is <50% of trailing 7-day median ({median_trailing:.1f})."
    return {
        "status": "PASS",
        "expected_date": expected_date,
        "latest_row_count": latest_count,
        "trailing_7d_median": median_trailing,
        "warning": warning,
    }


def gate_2_fanout(pre_join_rows: int | None, post_join_rows: int | None) -> dict[str, Any]:
    if pre_join_rows is None or post_join_rows is None:
        return {"status": "SKIPPED", "reason": "No --pre-join-rows / --post-join-rows provided."}
    fanout = post_join_rows > pre_join_rows
    ratio = round(post_join_rows / pre_join_rows, 4) if pre_join_rows > 0 else 0.0
    return {
        "status": "FAIL" if fanout else "PASS",
        "pre_join_rows": pre_join_rows,
        "post_join_rows": post_join_rows,
        "fanout_ratio": ratio,
    }


def gate_3_control_totals(
    df: pd.DataFrame,
    control_totals: dict[str, float],
    tolerance: float,
) -> dict[str, Any]:
    if not control_totals:
        return {"status": "SKIPPED", "reason": "No --control-totals provided."}
    checks = []
    all_pass = True
    for col, expected in control_totals.items():
        if col not in df.columns:
            checks.append({"column": col, "status": "FAIL", "reason": "Column missing"})
            all_pass = False
            continue
        actual = float(pd.to_numeric(df[col], errors="coerce").sum())
        delta = abs(actual - float(expected))
        ok = delta <= tolerance
        if not ok:
            all_pass = False
        checks.append(
            {
                "column": col,
                "expected_control_total": float(expected),
                "actual_report_total": round(actual, 6),
                "abs_delta": round(delta, 6),
                "tolerance": tolerance,
                "status": "PASS" if ok else "FAIL",
            }
        )
    return {"status": "PASS" if all_pass else "FAIL", "checks": checks}


def gate_4_parity(
    df: pd.DataFrame,
    summary_df: pd.DataFrame | None,
    ratio_checks: list[dict[str, str]],
    tolerance: float,
) -> dict[str, Any]:
    results: dict[str, Any] = {"cross_tab": [], "ratio_of_sums": []}
    all_pass = True

    if summary_df is not None:
        shared_numeric = [
            c
            for c in df.columns
            if c in summary_df.columns and pd.api.types.is_numeric_dtype(df[c]) and pd.api.types.is_numeric_dtype(summary_df[c])
        ]
        for col in shared_numeric:
            detail_sum = float(df[col].sum())
            summary_sum = float(summary_df[col].sum())
            delta = abs(detail_sum - summary_sum)
            ok = delta <= tolerance
            if not ok:
                all_pass = False
            results["cross_tab"].append(
                {
                    "column": col,
                    "detail_sum": round(detail_sum, 6),
                    "summary_sum": round(summary_sum, 6),
                    "abs_delta": round(delta, 6),
                    "status": "PASS" if ok else "FAIL",
                }
            )

    for rc in ratio_checks:
        name, num_col, den_col = rc["name"], rc["num"], rc["den"]
        if num_col not in df.columns or den_col not in df.columns:
            results["ratio_of_sums"].append({"ratio": name, "status": "FAIL", "reason": "Missing numerator/denominator"})
            all_pass = False
            continue
        total_num = float(pd.to_numeric(df[num_col], errors="coerce").sum())
        total_den = float(pd.to_numeric(df[den_col], errors="coerce").sum())
        expected_ratio = total_num / total_den if total_den != 0 else 0.0
        entry: dict[str, Any] = {
            "ratio": name,
            "ratio_of_sums": round(expected_ratio, 6),
            "status": "PASS",
        }
        if name in df.columns:
            row_mean = float(pd.to_numeric(df[name], errors="coerce").mean())
            entry["naive_avg_of_ratios"] = round(row_mean, 6)
            if abs(row_mean - expected_ratio) > tolerance:
                entry["note"] = "Naive AVG(pct) diverges from Ratio-of-Sums; always use SUM(num)/SUM(den) for totals."
        results["ratio_of_sums"].append(entry)

    if not results["cross_tab"] and not results["ratio_of_sums"]:
        return {"status": "SKIPPED", "reason": "No --summary-data or --ratio-checks provided."}
    return {"status": "PASS" if all_pass else "FAIL", **results}


def gate_5_anomalies(df: pd.DataFrame, z_threshold: float = 4.0) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    outliers: list[dict[str, Any]] = []

    for col in df.columns:
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            inf_count = int(np.isinf(series.to_numpy(dtype=float, na_value=np.nan)).sum())
            nan_count = int(series.isna().sum())
            if inf_count > 0:
                issues.append({"column": col, "type": "INF_VALUES", "count": inf_count})
            if nan_count > 0:
                issues.append({"column": col, "type": "NAN_NULL_VALUES", "count": nan_count})

            clean = series.dropna().astype(float)
            if len(clean) >= 5 and clean.std(ddof=0) > 0:
                z_scores = (clean - clean.mean()) / clean.std(ddof=0)
                extreme = clean[z_scores.abs() > z_threshold]
                if len(extreme) > 0:
                    outliers.append(
                        {
                            "column": col,
                            "outlier_count": int(len(extreme)),
                            "max_abs_z": round(float(z_scores.abs().max()), 2),
                            "sample_values": [round(float(v), 4) for v in extreme.head(5).tolist()],
                        }
                    )
        else:
            str_vals = series.astype(str).str.strip()
            err_hits = str_vals[str_vals.isin(EXCEL_ERROR_TOKENS)]
            if len(err_hits) > 0:
                issues.append(
                    {
                        "column": col,
                        "type": "EXCEL_ERROR_TOKENS",
                        "count": int(len(err_hits)),
                        "tokens": sorted(err_hits.unique().tolist()),
                    }
                )

    hard_fail = any(i["type"] in {"INF_VALUES", "EXCEL_ERROR_TOKENS"} for i in issues)
    return {
        "status": "FAIL" if hard_fail else "PASS",
        "row_count": int(len(df)),
        "issues": issues,
        "statistical_outliers": outliers,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Mandatory 5-Point Numbers Validation Gate.")
    parser.add_argument("--data", required=True, help="Path to primary query output (.csv/.json/.parquet/.xlsx).")
    parser.add_argument("--summary-data", default=None, help="Optional summary tab dataset for cross-tab parity.")
    parser.add_argument("--freshness-date-col", default=None, help="Date column name for Gate 1 freshness check.")
    parser.add_argument("--expected-date", default=None, help="Expected latest YYYY-MM-DD date for Gate 1.")
    parser.add_argument("--pre-join-rows", type=int, default=None, help="Base pre-join row count for Gate 2.")
    parser.add_argument("--post-join-rows", type=int, default=None, help="Post-join row count for Gate 2.")
    parser.add_argument("--control-totals", default="{}", help='JSON dict of {"col": expected_sum} for Gate 3.')
    parser.add_argument("--ratio-checks", default="[]", help='JSON list of {"name","num","den"} for Gate 4.')
    parser.add_argument("--tolerance", type=float, default=0.01, help="Reconciliation tolerance (default: 0.01).")
    parser.add_argument("--report-out", default=None, help="Optional JSON audit log output path.")
    args = parser.parse_args()

    df = load_dataset(Path(args.data))
    summary_df = load_dataset(Path(args.summary_data)) if args.summary_data else None
    control_totals = json.loads(args.control_totals)
    ratio_checks = json.loads(args.ratio_checks)

    audit = {
        "dataset": args.data,
        "gates": {
            "1_etl_freshness": gate_1_freshness(df, args.freshness_date_col, args.expected_date),
            "2_join_fanout": gate_2_fanout(args.pre_join_rows, args.post_join_rows),
            "3_control_totals": gate_3_control_totals(df, control_totals, args.tolerance),
            "4_cross_tab_and_ratio_parity": gate_4_parity(df, summary_df, ratio_checks, args.tolerance),
            "5_anomaly_and_null_scan": gate_5_anomalies(df),
        },
    }

    statuses = [g["status"] for g in audit["gates"].values()]
    overall = "FAIL" if "FAIL" in statuses else "PASS"
    audit["overall_status"] = overall

    rendered = json.dumps(audit, indent=2)
    if args.report_out:
        out_path = Path(args.report_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0 if overall == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
