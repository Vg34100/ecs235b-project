import argparse
import json
from collections import Counter
from pathlib import Path

from src.detector import detect_case
from src.pipeline import LLMRunner, get_ablation_source_candidates
from src.traces import PolicyTrace, get_available_sources, get_case_prompt, get_primary_prompt_source


def load_cases(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def material_answer_change(a: str, b: str) -> bool:
    # Very simple rule for MVP: exact string mismatch means changed output.
    return a.strip() != b.strip()


def run_ablation_checks(
    runner: LLMRunner,
    case: dict,
    base_answer: str,
    max_new_tokens: int,
) -> dict[str, bool]:
    influence = {}
    for source_name in get_ablation_source_candidates(case):
        ablated = runner.run_case(case, source_overrides={source_name: ""}, max_new_tokens=max_new_tokens)
        influence[source_name] = material_answer_change(base_answer, ablated.answer)
    return influence


def build_final_used_sources(
    case: dict,
    reported_sources: list[str],
    ablation_influence: dict[str, bool],
) -> list[str]:
    # Keep the merge rule simple and stable for now.
    merged_sources = set(reported_sources)
    merged_sources.add(get_primary_prompt_source(case))
    for source_name, changed in ablation_influence.items():
        if changed:
            merged_sources.add(source_name)
    return sorted(merged_sources)


def build_trace(
    case: dict,
    model_name: str,
    base_answer: str,
    reported_sources: list[str],
    ablation_influence: dict[str, bool],
    raw_output: str,
    run_reason: str,
) -> PolicyTrace:
    inferred_sources = sorted([source_name for source_name, changed in ablation_influence.items() if changed])
    final_used_sources = build_final_used_sources(case, reported_sources, ablation_influence)
    detection = detect_case(case, final_used_sources, base_answer)

    return PolicyTrace(
        case_id=detection.case_id,
        model_name=model_name,
        prompt=get_case_prompt(case),
        available_sources=get_available_sources(case),
        required_sources=list(case.get("required_sources", [])),
        forbidden_sources=list(case.get("forbidden_sources", [])),
        model_answer=detection.answer,
        used_sources_reported=sorted(reported_sources),
        used_sources_inferred=inferred_sources,
        final_used_sources=detection.used_sources,
        violation=detection.violation,
        violation_types=detection.violation_types,
        policy_explanation=detection.explanation,
        ablation_influence=ablation_influence,
        raw_output=raw_output,
        run_reason=run_reason,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Quick MVP: audit information flow in an LLM pipeline")
    parser.add_argument("--cases", default="data/cases/cases.json", help="Path to case JSON file")
    parser.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct", help="Hugging Face model id")
    parser.add_argument("--mock", action="store_true", help="Use mock mode instead of loading model")
    parser.add_argument("--limit", type=int, default=0, help="Only run first N cases (0 means all)")
    parser.add_argument("--skip-ablations", action="store_true", help="Skip source ablation checks for faster runs")
    parser.add_argument("--max-new-tokens", type=int, default=120, help="Generation budget per call")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    cases_path = project_root / args.cases

    cases = load_cases(cases_path)
    if args.limit and args.limit > 0:
        cases = cases[: args.limit]

    runner = LLMRunner(model_id=args.model, mock_mode=args.mock)
    runner.load()

    traces = []
    violation_counter = Counter()

    for case in cases:
        base = runner.run_case(case, max_new_tokens=args.max_new_tokens)
        if args.skip_ablations:
            ablation_influence = {source_name: False for source_name in get_ablation_source_candidates(case)}
        else:
            ablation_influence = run_ablation_checks(
                runner,
                case,
                base.answer,
                max_new_tokens=args.max_new_tokens,
            )

        trace = build_trace(
            case=case,
            model_name=args.model if not args.mock else "mock",
            base_answer=base.answer,
            reported_sources=base.used_sources,
            ablation_influence=ablation_influence,
            raw_output=base.raw_output,
            run_reason=base.reason,
        )

        for vt in trace.violation_types:
            violation_counter[vt] += 1

        traces.append(trace)

    total = len(traces)
    violations = sum(1 for trace in traces if trace.violation)
    compliant = total - violations

    outputs_dir = project_root / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    trace_json_path = outputs_dir / "policy_traces.json"
    with trace_json_path.open("w", encoding="utf-8") as f:
        json.dump([trace.to_dict() for trace in traces], f, indent=2)

    summary_json_path = outputs_dir / "mvp_summary.json"
    with summary_json_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "total_cases": total,
                "compliant_cases": compliant,
                "violating_cases": violations,
                "violation_counts": dict(violation_counter),
                "trace_file": str(trace_json_path.name),
                "results": [trace.to_dict() for trace in traces],
            },
            f,
            indent=2,
        )

    summary_md_path = outputs_dir / "mvp_summary.md"
    with summary_md_path.open("w", encoding="utf-8") as f:
        f.write("# Quick MVP Summary\n\n")
        f.write(f"- Total cases: {total}\n")
        f.write(f"- Compliant cases: {compliant}\n")
        f.write(f"- Violating cases: {violations}\n")
        f.write(f"- Violation counts: {dict(violation_counter)}\n\n")

        f.write("## Example Results\n")
        for trace in traces[:5]:
            f.write(f"- {trace.case_id}: violation={trace.violation} ")
            f.write(f"types={trace.violation_types} ")
            f.write(f"final_used={trace.final_used_sources}\n")
            f.write(f"  explanation: {trace.policy_explanation}\n")

    print(f"Saved {trace_json_path}")
    print(f"Saved {summary_json_path}")
    print(f"Saved {summary_md_path}")
    print(f"Total={total}, Compliant={compliant}, Violating={violations}")


if __name__ == "__main__":
    main()
