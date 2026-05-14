import argparse
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_metrics(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_user_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def violation_count(row: dict[str, Any], key: str) -> int:
    return int(row.get("violation_counts", {}).get(key, 0))


def render_table(metrics: list[dict[str, Any]], title: str) -> str:
    lines = [
        f"# {title}",
        "",
        "| Run | Model | Quant | Total | Compliant | Violating | Correct | Correct+Compliant | Correct+Violating | Consistency | Forbidden |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in metrics:
        lines.append(
            "| {run} | {model} | {quant} | {total} | {compliant} | {violating} | {correct} | {cc} | {cv} | {consistency} | {forbidden} |".format(
                run=row.get("run_name", ""),
                model=row.get("model", ""),
                quant=row.get("quantization", ""),
                total=row.get("total_cases", 0),
                compliant=row.get("compliant_cases", 0),
                violating=row.get("violating_cases", 0),
                correct=row.get("answer_correct", 0),
                cc=row.get("correct_and_compliant", 0),
                cv=row.get("correct_but_violating", 0),
                consistency=violation_count(row, "consistency_violation"),
                forbidden=violation_count(row, "forbidden_source_used"),
            )
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a markdown comparison table from collected metrics")
    parser.add_argument(
        "--metrics-json",
        default="outputs/analysis/comparison_metrics.json",
        help="Metrics JSON produced by collect_comparison_metrics.py",
    )
    parser.add_argument(
        "--write-output",
        default="outputs/analysis/mmmu_comparison_table.md",
        help="Where to write the markdown table",
    )
    parser.add_argument(
        "--title",
        default="Comparison Table",
        help="Markdown title to place above the rendered table",
    )
    args = parser.parse_args()

    metrics = load_metrics(resolve_user_path(args.metrics_json))
    rendered = render_table(metrics, args.title)

    output_path = resolve_user_path(args.write_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")

    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
