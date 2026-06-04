import argparse
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def resolve_user_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def load_metrics(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def violation_count(row: dict[str, Any], key: str) -> int:
    return int(row.get("violation_counts", {}).get(key, 0))


def run_label(row: dict[str, Any]) -> str:
    # Keep labels short enough to survive a paper-sized figure.
    benchmark = str(row.get("benchmark", ""))
    subject = str(row.get("subject", ""))
    setting = str(row.get("setting", ""))
    if benchmark == "MMMU" and subject:
        return f"{subject} {setting}"
    if benchmark == "InjecAgent":
        return f"InjecAgent {setting}"
    if benchmark == "HybridQA":
        return "HybridQA"
    return str(row.get("run_name", ""))


def metric_triplet(row: dict[str, Any]) -> list[tuple[str, float, str]]:
    # This first figure only needs the three rates that best explain the project:
    # compliance, answer correctness, and forbidden-source pressure.
    total = max(int(row.get("total_cases", 0)), 1)
    compliant_rate = int(row.get("compliant_cases", 0)) / total
    correct_rate = int(row.get("answer_correct", 0)) / total
    forbidden_rate = violation_count(row, "forbidden_source_used") / total
    return [
        ("Compliant", compliant_rate, "#2E8B57"),
        ("Correct", correct_rate, "#1F4E79"),
        ("Forbidden", forbidden_rate, "#B22222"),
    ]


def sort_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("benchmark", "")),
        str(row.get("subject", "")),
        str(row.get("run_name", "")),
    )


def render_svg(payload: dict[str, Any], title: str) -> str:
    rows = sorted(payload.get("runs", []), key=sort_key)
    if not rows:
        return "<svg xmlns='http://www.w3.org/2000/svg' width='800' height='200'></svg>\n"

    width = 1200
    height = 520
    margin_left = 90
    margin_right = 40
    margin_top = 70
    margin_bottom = 150
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom
    group_width = chart_width / len(rows)
    bar_width = min(34, group_width / 4)
    max_bar_height = chart_height

    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>",
        "<style>",
        "text { font-family: 'DejaVu Sans Mono', monospace; fill: #18212b; }",
        ".axis { stroke: #475569; stroke-width: 1; }",
        ".grid { stroke: #cbd5e1; stroke-width: 1; }",
        ".label { font-size: 12px; }",
        ".tick { font-size: 11px; }",
        ".title { font-size: 20px; font-weight: 700; }",
        ".legend { font-size: 12px; }",
        "</style>",
        f"<rect x='0' y='0' width='{width}' height='{height}' fill='#f8fafc'/>",
        f"<text class='title' x='{margin_left}' y='35'>{title}</text>",
    ]

    chart_x0 = margin_left
    chart_y0 = margin_top
    chart_y1 = margin_top + chart_height

    for pct in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = chart_y1 - pct * chart_height
        parts.append(f"<line class='grid' x1='{chart_x0}' y1='{y}' x2='{chart_x0 + chart_width}' y2='{y}'/>")
        parts.append(f"<text class='tick' x='{chart_x0 - 10}' y='{y + 4}' text-anchor='end'>{int(pct * 100)}%</text>")

    parts.append(f"<line class='axis' x1='{chart_x0}' y1='{chart_y0}' x2='{chart_x0}' y2='{chart_y1}'/>")
    parts.append(f"<line class='axis' x1='{chart_x0}' y1='{chart_y1}' x2='{chart_x0 + chart_width}' y2='{chart_y1}'/>")

    legend_items = [("Compliant", "#2E8B57"), ("Correct", "#1F4E79"), ("Forbidden", "#B22222")]
    legend_x = chart_x0
    legend_y = 52
    for idx, (name, color) in enumerate(legend_items):
        x = legend_x + idx * 140
        parts.append(f"<rect x='{x}' y='{legend_y - 10}' width='14' height='14' fill='{color}' rx='2'/>")
        parts.append(f"<text class='legend' x='{x + 22}' y='{legend_y + 1}'>{name}</text>")

    for idx, row in enumerate(rows):
        group_x = chart_x0 + idx * group_width + group_width / 2
        metrics = metric_triplet(row)
        # Use the same ordering everywhere so the figure is readable without
        # re-learning the color mapping row by row.
        start_x = group_x - ((len(metrics) - 1) * bar_width * 1.4) / 2

        for bar_idx, (_, value, color) in enumerate(metrics):
            bar_h = value * max_bar_height
            x = start_x + bar_idx * bar_width * 1.4
            y = chart_y1 - bar_h
            parts.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{bar_width:.1f}' height='{bar_h:.1f}' fill='{color}' rx='3'/>")

        label = run_label(row)
        label_x = group_x
        label_y = chart_y1 + 20
        parts.append(
            f"<text class='label' x='{label_x:.1f}' y='{label_y}' text-anchor='end' transform='rotate(-35 {label_x:.1f},{label_y})'>{label}</text>"
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a cross-benchmark SVG figure from collected metrics")
    parser.add_argument(
        "--metrics-json",
        default="outputs/analysis/cross_benchmark_metrics.json",
        help="Cross-benchmark metrics JSON produced by collect_cross_benchmark_metrics.py",
    )
    parser.add_argument(
        "--write-output",
        default="outputs/analysis/cross_benchmark_summary.svg",
        help="Where to write the SVG figure",
    )
    parser.add_argument(
        "--title",
        default="Cross-Benchmark Summary",
        help="Figure title",
    )
    args = parser.parse_args()

    payload = load_metrics(resolve_user_path(args.metrics_json))
    rendered = render_svg(payload, args.title)

    output_path = resolve_user_path(args.write_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")

    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
