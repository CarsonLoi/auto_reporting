# Visualization & Executive Design Standards

> Maintained by `05-report-and-viz-builder` and user preferences.

## Corporate Color Palette (Colorblind-Safe, Executive BI)

| Role | Hex | Usage |
| :--- | :--- | :--- |
| **Primary Navy** | `#1B365D` | Primary bars/lines, table headers, titles |
| **Secondary Teal** | `#008080` | Secondary series, comparison periods |
| **Accent Amber** | `#D97706` | Highlighted callouts, targets, thresholds |
| **Positive Green** | `#15803D` | Favorable YoY/WoW variance |
| **Negative Crimson** | `#B91C1C` | Unfavorable variance, anomalies, alerts |
| **Neutral Slate** | `#475569` | Prior-period baselines, secondary text |
| **Light Grid / Zebra** | `#E2E8F0` / `#F8FAFC` | Subtle gridlines, alternating table rows |

## Typography & Layout

- **Font Stack:** `Inter`, `Segoe UI`, `Arial`, `sans-serif` (monospace `Consolas` / `JetBrains Mono` for tabular numbers in HTML).
- **Title Hierarchy:** Action-oriented headline (14–16pt bold) + subtitle stating exact date range, filters, and units (10–11pt slate).
- **Data Ink Ratio:** Remove top/right chart spines, use faint horizontal gridlines only, place direct data labels on key bars/endpoints, and avoid 3D charts or pie charts with >4 slices.

## Integrity Rules

1. **Zero-Baseline Rule:** Bar charts and area charts MUST start at `0`. Line charts may use a tight y-axis only when clearly annotated.
2. **Compact Axis Formatting:** Use `K`, `M`, `B` suffixes on axes (`$1.2M`) while keeping exact values in hover tooltips and companion tables.
3. **Chart Selection Guide:**
   - Trend over time → Line chart (or bar + line dual-axis only when scales genuinely differ and both axes are clearly labeled).
   - Category comparison → Horizontal bar chart sorted descending by value.
   - Composition over time → Stacked bar (≤5 categories; group tail into `Other`).
   - Distribution / outliers → Box/violin or histogram.
   - Relationship / correlation → Scatter plot with OLS trendline (`statsmodels`).
4. **High-DPI Export:** Export static figures at `300 DPI` PNG or vector SVG/PDF.
