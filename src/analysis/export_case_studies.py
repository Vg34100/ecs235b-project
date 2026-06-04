import argparse
import json
import sys
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


def infer_benchmark(run_name: str, case_map: dict[str, dict[str, Any]]) -> str:
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


def preview_value(value: Any, limit: int = 220) -> str:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=True)
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def source_previews(case: dict[str, Any]) -> dict[str, str]:
    previews: dict[str, str] = {}
    for name, value in case.get("sources", {}).items():
        previews[name] = preview_value(value, limit=240)
    return previews


def image_info(case: dict[str, Any]) -> dict[str, Any]:
    image_evidence = case.get("sources", {}).get("image_evidence", {})
    images = image_evidence.get("images", []) if isinstance(image_evidence, dict) else []
    return {
        "image_paths": [str(img.get("path", "")) for img in images if img.get("path")],
        "img_type": list(image_evidence.get("img_type", [])) if isinstance(image_evidence, dict) else [],
        "subfield": str(image_evidence.get("subfield", "")) if isinstance(image_evidence, dict) else "",
    }


def infer_prompt_mode(run_name: str) -> str:
    lowered = run_name.lower()
    if "hidden" in lowered:
        return "hidden"
    if "explicit" in lowered:
        return "explicit"
    return "default"


def expected_answer(case: dict[str, Any]) -> str:
    return str(case.get("expected_behavior", {}).get("expected_answer", "")).strip()


def trace_correctness(trace: dict[str, Any], case: dict[str, Any]) -> bool:
    exp = expected_answer(case)
    if not exp:
        return False
    return answer_matches_expected(str(trace.get("model_answer", "")), exp)


def make_case_entry(
    benchmark: str,
    category: str,
    run_name: str,
    manifest: dict[str, Any],
    trace: dict[str, Any],
    case: dict[str, Any],
) -> dict[str, Any]:
    return {
        "benchmark": benchmark,
        "category": category,
        "run_name": run_name,
        "model": manifest.get("model", ""),
        "quantization": manifest.get("quantization", ""),
        "prompt_mode": infer_prompt_mode(run_name),
        "case_id": trace.get("case_id", ""),
        "domain": trace.get("domain", ""),
        "task_type": case.get("task_type", ""),
        "prompt": trace.get("prompt", ""),
        "expected_answer": expected_answer(case),
        "model_answer": trace.get("model_answer", ""),
        "is_correct": trace_correctness(trace, case),
        "violation": bool(trace.get("violation", False)),
        "violation_types": list(trace.get("violation_types", [])),
        "policy_explanation": trace.get("policy_explanation", ""),
        "required_sources": list(trace.get("required_sources", [])),
        "forbidden_sources": list(trace.get("forbidden_sources", [])),
        "used_sources_reported": list(trace.get("used_sources_reported", [])),
        "used_sources_inferred": list(trace.get("used_sources_inferred", [])),
        "final_used_sources": list(trace.get("final_used_sources", [])),
        "run_reason": trace.get("run_reason", ""),
        "source_previews": source_previews(case),
        "image_info": image_info(case),
        "notes": manifest.get("notes", ""),
    }


def select_injecagent_hidden_failures(run_dir: Path, limit: int) -> list[dict[str, Any]]:
    manifest = load_manifest(run_dir)
    case_map = load_case_map(run_dir)
    traces = load_json(run_dir / "policy_traces.json")
    run_name = manifest.get("run_name", run_dir.name)
    benchmark = infer_benchmark(run_name, case_map)

    selected = []
    for trace in traces:
        if not trace.get("violation", False):
            continue
        case = case_map.get(trace["case_id"])
        if case is None:
            continue
        selected.append(make_case_entry(benchmark, "injecagent_hidden_failures", run_name, manifest, trace, case))
        if len(selected) >= limit:
            break
    return selected


def select_hybridqa_correct_but_violating(run_dir: Path, limit: int) -> list[dict[str, Any]]:
    manifest = load_manifest(run_dir)
    case_map = load_case_map(run_dir)
    traces = load_json(run_dir / "policy_traces.json")
    run_name = manifest.get("run_name", run_dir.name)
    benchmark = infer_benchmark(run_name, case_map)

    selected = []
    for trace in traces:
        if not trace.get("violation", False):
            continue
        case = case_map.get(trace["case_id"])
        if case is None:
            continue
        if not trace_correctness(trace, case):
            continue
        selected.append(make_case_entry(benchmark, "hybridqa_correct_but_violating", run_name, manifest, trace, case))
        if len(selected) >= limit:
            break
    return selected


def select_mmmu_forbidden_cases(run_dirs: list[Path], limit_per_run: int) -> list[dict[str, Any]]:
    selected = []
    for run_dir in run_dirs:
        manifest = load_manifest(run_dir)
        case_map = load_case_map(run_dir)
        traces = load_json(run_dir / "policy_traces.json")
        run_name = manifest.get("run_name", run_dir.name)
        benchmark = infer_benchmark(run_name, case_map)

        count = 0
        for trace in traces:
            if "forbidden_source_used" not in trace.get("violation_types", []):
                continue
            case = case_map.get(trace["case_id"])
            if case is None:
                continue
            selected.append(make_case_entry(benchmark, "mmmu_forbidden_following", run_name, manifest, trace, case))
            count += 1
            if count >= limit_per_run:
                break
    return selected


def build_payload(
    injecagent_run_dir: Path,
    hybridqa_run_dir: Path,
    mmmu_run_dirs: list[Path],
    injecagent_limit: int,
    hybridqa_limit: int,
    mmmu_limit_per_run: int,
) -> dict[str, Any]:
    case_studies = []
    case_studies.extend(select_injecagent_hidden_failures(injecagent_run_dir, injecagent_limit))
    case_studies.extend(select_hybridqa_correct_but_violating(hybridqa_run_dir, hybridqa_limit))
    case_studies.extend(select_mmmu_forbidden_cases(mmmu_run_dirs, mmmu_limit_per_run))

    return {
        "generated_from_runs": {
            "injecagent": str(injecagent_run_dir),
            "hybridqa": str(hybridqa_run_dir),
            "mmmu": [str(path) for path in mmmu_run_dirs],
        },
        "case_studies": case_studies,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Case Studies", ""]
    for case in payload.get("case_studies", []):
        lines.append(f"## {case['benchmark']} / {case['category']} / {case['case_id']}")
        lines.append("")
        lines.append(f"- Run: `{case['run_name']}`")
        lines.append(f"- Domain: `{case['domain']}`")
        lines.append(f"- Correct: `{case['is_correct']}`")
        lines.append(f"- Violation Types: `{case['violation_types']}`")
        lines.append(f"- Final Used Sources: `{case['final_used_sources']}`")
        lines.append(f"- Prompt: {case['prompt']}")
        lines.append(f"- Expected Answer: `{case['expected_answer']}`")
        lines.append(f"- Model Answer: `{case['model_answer']}`")
        lines.append(f"- Policy Explanation: {case['policy_explanation']}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export representative case-study artifacts from archived runs")
    parser.add_argument("--injecagent-run-dir", required=True, help="Archived InjecAgent run directory")
    parser.add_argument("--hybridqa-run-dir", required=True, help="Archived HybridQA run directory")
    parser.add_argument(
        "--mmmu-run-dir",
        action="append",
        required=True,
        help="Archived MMMU run directory; repeat for multiple MMMU runs",
    )
    parser.add_argument("--injecagent-limit", type=int, default=2, help="Number of InjecAgent failure cases to export")
    parser.add_argument("--hybridqa-limit", type=int, default=2, help="Number of HybridQA correct-but-violating cases")
    parser.add_argument("--mmmu-limit-per-run", type=int, default=2, help="Number of MMMU forbidden cases per run")
    parser.add_argument(
        "--write-json",
        default="outputs/analysis/case_studies.json",
        help="Where to write the case-study JSON payload",
    )
    parser.add_argument(
        "--write-markdown",
        default="outputs/analysis/case_studies.md",
        help="Where to write the case-study markdown summary",
    )
    args = parser.parse_args()

    payload = build_payload(
        injecagent_run_dir=resolve_user_path(args.injecagent_run_dir),
        hybridqa_run_dir=resolve_user_path(args.hybridqa_run_dir),
        mmmu_run_dirs=[resolve_user_path(path) for path in args.mmmu_run_dir],
        injecagent_limit=args.injecagent_limit,
        hybridqa_limit=args.hybridqa_limit,
        mmmu_limit_per_run=args.mmmu_limit_per_run,
    )

    json_path = resolve_user_path(args.write_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_path = resolve_user_path(args.write_markdown)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(payload), encoding="utf-8")

    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    print(f"case studies exported: {len(payload['case_studies'])}")


if __name__ == "__main__":
    main()
