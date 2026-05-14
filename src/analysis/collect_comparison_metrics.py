import argparse
import json
from collections import Counter
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.policies import answer_matches_expected


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_user_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def load_case_map(run_dir: Path) -> dict[str, dict[str, Any]]:
    manifest_path = run_dir / "manifest.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {}

    snapshot_name = manifest.get("case_snapshot", "")
    if snapshot_name:
        snapshot_path = run_dir / snapshot_name
        if snapshot_path.exists():
            cases = load_json(snapshot_path)
            return {case["case_id"]: case for case in cases}

    return {}


def compute_metrics(run_dir: Path) -> dict[str, Any]:
    traces = load_json(run_dir / "policy_traces.json")
    case_map = load_case_map(run_dir)
    manifest = load_json(run_dir / "manifest.json") if (run_dir / "manifest.json").exists() else {}

    violation_counts = Counter()
    total = len(traces)
    compliant = 0
    answer_correct = 0
    correct_and_compliant = 0
    correct_but_violating = 0

    for trace in traces:
        if not trace.get("violation", False):
            compliant += 1
        for violation_type in trace.get("violation_types", []):
            violation_counts[violation_type] += 1

        case = case_map.get(trace["case_id"])
        expected_answer = ""
        if case is not None:
            expected_answer = str(case.get("expected_behavior", {}).get("expected_answer", "")).strip()

        is_correct = bool(expected_answer and answer_matches_expected(trace.get("model_answer", ""), expected_answer))
        if is_correct:
            answer_correct += 1
            if trace.get("violation", False):
                correct_but_violating += 1
            else:
                correct_and_compliant += 1

    return {
        "run_name": manifest.get("run_name", run_dir.name),
        "model": manifest.get("model", ""),
        "quantization": manifest.get("quantization", ""),
        "notes": manifest.get("notes", ""),
        "total_cases": total,
        "compliant_cases": compliant,
        "violating_cases": total - compliant,
        "answer_correct": answer_correct,
        "correct_and_compliant": correct_and_compliant,
        "correct_but_violating": correct_but_violating,
        "violation_counts": dict(sorted(violation_counts.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect comparison metrics from archived run folders")
    parser.add_argument(
        "--run-dir",
        action="append",
        required=True,
        help="Archived run directory under outputs/archive to summarize; repeat for multiple runs",
    )
    parser.add_argument(
        "--write-output",
        default="outputs/analysis/comparison_metrics.json",
        help="Where to write the collected metrics JSON",
    )
    args = parser.parse_args()

    run_dirs = [resolve_user_path(run_dir) for run_dir in args.run_dir]
    metrics = [compute_metrics(run_dir) for run_dir in run_dirs]

    output_path = resolve_user_path(args.write_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"wrote {output_path}")
    print(f"runs summarized: {len(metrics)}")
    for row in metrics:
        print(
            f"- {row['run_name']}: compliant={row['compliant_cases']}/{row['total_cases']}, "
            f"correct={row['answer_correct']}/{row['total_cases']}"
        )


if __name__ == "__main__":
    main()
