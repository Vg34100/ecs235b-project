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


def correctness_cell(row: dict[str, Any]) -> str:
    scored = int(row.get("answer_scored_cases", 0))
    correct = int(row.get("answer_correct", 0))
    if scored == 0:
        return "N/A"
    return f"{correct}/{scored}"


def sort_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("benchmark", "")),
        str(row.get("subject", "")),
        str(row.get("run_name", "")),
    )


def render_table(payload: dict[str, Any], title: str) -> str:
    rows = sorted(payload.get("runs", []), key=sort_key)
    lines = [
        f"# {title}",
        "",
        "| Benchmark | Subject | Run | Setting | Model | Quant | Total | Compliant | Correct | Correct+Compliant | Correct+Violating | Forbidden | Missing Required | Consistency |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for row in rows:
        lines.append(
            "| {benchmark} | {subject} | {run} | {setting} | {model} | {quant} | {total} | {compliant} | {correct} | {cc} | {cv} | {forbidden} | {missing} | {consistency} |".format(
                benchmark=row.get("benchmark", ""),
                subject=row.get("subject", ""),
                run=row.get("run_name", ""),
                setting=row.get("setting", ""),
                model=row.get("model", ""),
                quant=row.get("quantization", ""),
                total=row.get("total_cases", 0),
                compliant=row.get("compliant_cases", 0),
                correct=correctness_cell(row),
                cc=row.get("correct_and_compliant", 0),
                cv=row.get("correct_but_violating", 0),
                forbidden=violation_count(row, "forbidden_source_used"),
                missing=violation_count(row, "missing_required_source"),
                consistency=violation_count(row, "consistency_violation"),
            )
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a cross-benchmark markdown summary table")
    parser.add_argument(
        "--metrics-json",
        default="outputs/analysis/cross_benchmark_metrics.json",
        help="Cross-benchmark metrics JSON produced by collect_cross_benchmark_metrics.py",
    )
    parser.add_argument(
        "--write-output",
        default="outputs/analysis/cross_benchmark_summary.md",
        help="Where to write the markdown summary table",
    )
    parser.add_argument(
        "--title",
        default="Cross-Benchmark Summary",
        help="Markdown title to place above the rendered table",
    )
    args = parser.parse_args()

    payload = load_metrics(resolve_user_path(args.metrics_json))
    rendered = render_table(payload, args.title)

    output_path = resolve_user_path(args.write_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")

    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
