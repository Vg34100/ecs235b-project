import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.policies import answer_matches_expected


def resolve_user_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return {}
    return load_json(manifest_path)


def load_case_map(run_dir: Path) -> dict[str, dict[str, Any]]:
    manifest = load_manifest(run_dir)
    snapshot_name = manifest.get("case_snapshot", "")
    if not snapshot_name:
        return {}

    snapshot_path = run_dir / snapshot_name
    if not snapshot_path.exists():
        return {}

    cases = load_json(snapshot_path)
    return {case["case_id"]: case for case in cases}


def infer_benchmark_family(run_name: str, case_map: dict[str, dict[str, Any]]) -> str:
    if case_map:
        sample_case = next(iter(case_map.values()))
        dataset_source = str(sample_case.get("dataset_source", "")).lower()
        task_type = str(sample_case.get("task_type", "")).lower()
        if "injecagent" in dataset_source:
            return "InjecAgent"
        if "hybridqa" in dataset_source or task_type == "table_text_reasoning":
            return "HybridQA"
        if "mmmu" in dataset_source or task_type == "image_text_reasoning":
            return "MMMU"

    lowered = run_name.lower()
    if "injecagent" in lowered:
        return "InjecAgent"
    if "hybridqa" in lowered:
        return "HybridQA"
    if "mmmu" in lowered:
        return "MMMU"
    return "Unknown"


def infer_setting_label(run_name: str) -> str:
    lowered = run_name.lower()
    if "hidden" in lowered:
        return "hidden"
    if "explicit" in lowered:
        return "explicit"
    if "forbidden" in lowered:
        return "forbidden"
    if "base" in lowered:
        return "base"
    return "default"


def infer_subject_label(run_name: str, case_map: dict[str, dict[str, Any]]) -> str:
    lowered = run_name.lower()
    if "accounting" in lowered:
        return "Accounting"
    if "computer_science" in lowered:
        return "Computer_Science"

    if case_map:
        sample_case = next(iter(case_map.values()))
        domain = str(sample_case.get("domain", ""))
        if domain == "computer_science_vision":
            return "Computer_Science"
        if domain == "accounting_vision":
            return "Accounting"
    return ""


def compute_metrics(run_dir: Path) -> dict[str, Any]:
    traces = load_json(run_dir / "policy_traces.json")
    manifest = load_manifest(run_dir)
    case_map = load_case_map(run_dir)

    total = len(traces)
    compliant = 0
    correct = 0
    answer_scored_cases = 0
    correct_and_compliant = 0
    correct_but_violating = 0
    violation_counts: Counter[str] = Counter()
    domain_counts: Counter[str] = Counter()

    for trace in traces:
        domain_counts[str(trace.get("domain", "unknown"))] += 1
        is_violation = bool(trace.get("violation", False))
        if not is_violation:
            compliant += 1

        for violation_type in trace.get("violation_types", []):
            violation_counts[str(violation_type)] += 1

        case = case_map.get(trace["case_id"])
        expected_answer = ""
        if case is not None:
            expected_answer = str(case.get("expected_behavior", {}).get("expected_answer", "")).strip()

        if expected_answer:
            answer_scored_cases += 1
        is_correct = bool(expected_answer and answer_matches_expected(str(trace.get("model_answer", "")), expected_answer))
        if is_correct:
            correct += 1
            if is_violation:
                correct_but_violating += 1
            else:
                correct_and_compliant += 1

    run_name = manifest.get("run_name", run_dir.name)
    benchmark = infer_benchmark_family(run_name, case_map)
    subject = infer_subject_label(run_name, case_map)
    setting = infer_setting_label(run_name)

    return {
        "run_name": run_name,
        "benchmark": benchmark,
        "subject": subject,
        "setting": setting,
        "model": manifest.get("model", ""),
        "quantization": manifest.get("quantization", ""),
        "notes": manifest.get("notes", ""),
        "total_cases": total,
        "compliant_cases": compliant,
        "violating_cases": total - compliant,
        "answer_scored_cases": answer_scored_cases,
        "answer_correct": correct,
        "correct_and_compliant": correct_and_compliant,
        "correct_but_violating": correct_but_violating,
        "violation_counts": dict(sorted(violation_counts.items())),
        "domain_counts": dict(sorted(domain_counts.items())),
        "archive_dir": str(run_dir),
    }


def build_output(run_dirs: list[Path]) -> dict[str, Any]:
    runs = [compute_metrics(run_dir) for run_dir in run_dirs]
    return {
        "generated_from_runs": [str(run_dir) for run_dir in run_dirs],
        "runs": runs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect cross-benchmark metrics from archived run folders")
    parser.add_argument(
        "--run-dir",
        action="append",
        required=True,
        help="Archived run directory under outputs/archive to summarize; repeat for multiple runs",
    )
    parser.add_argument(
        "--write-output",
        default="outputs/analysis/cross_benchmark_metrics.json",
        help="Where to write the collected metrics JSON",
    )
    args = parser.parse_args()

    run_dirs = [resolve_user_path(run_dir) for run_dir in args.run_dir]
    payload = build_output(run_dirs)

    output_path = resolve_user_path(args.write_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"wrote {output_path}")
    print(f"runs summarized: {len(payload['runs'])}")
    for row in payload["runs"]:
        print(
            f"- {row['benchmark']} / {row['run_name']}: "
            f"compliant={row['compliant_cases']}/{row['total_cases']}, "
            f"correct={row['answer_correct']}/{row['total_cases']}"
        )


if __name__ == "__main__":
    main()
