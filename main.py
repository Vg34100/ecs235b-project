import argparse
import json
from collections import Counter
from pathlib import Path

from src.detector import detect_case
from src.pipeline import LLMRunner


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

    no_image = runner.run_case(case, source_overrides={"image_evidence": ""}, max_new_tokens=max_new_tokens)
    influence["image_evidence"] = material_answer_change(base_answer, no_image.answer)

    no_context = runner.run_case(case, source_overrides={"retrieved_context": ""}, max_new_tokens=max_new_tokens)
    influence["retrieved_context"] = material_answer_change(base_answer, no_context.answer)

    no_hidden = runner.run_case(case, source_overrides={"hidden_metadata": ""}, max_new_tokens=max_new_tokens)
    influence["hidden_metadata"] = material_answer_change(base_answer, no_hidden.answer)

    return influence


def main() -> None:
    parser = argparse.ArgumentParser(description="Quick MVP: audit information flow in an LLM pipeline")
    parser.add_argument("--cases", default="src/data/cases.json", help="Path to case JSON file")
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

    results = []
    violation_counter = Counter()

    for case in cases:
        base = runner.run_case(case, max_new_tokens=args.max_new_tokens)
        if args.skip_ablations:
            ablation_influence = {
                "image_evidence": False,
                "retrieved_context": False,
                "hidden_metadata": False,
            }
        else:
            ablation_influence = run_ablation_checks(
                runner,
                case,
                base.answer,
                max_new_tokens=args.max_new_tokens,
            )

        # Combine self-reported and ablation-based sources
        merged_sources = set(base.used_sources)
        for source_name, changed in ablation_influence.items():
            if changed:
                merged_sources.add(source_name)

        detection = detect_case(case, sorted(merged_sources), base.answer)
        for vt in detection.violation_types:
            violation_counter[vt] += 1

        result_row = {
            "case_id": detection.case_id,
            "answer": detection.answer,
            "used_sources": detection.used_sources,
            "ablation_influence": ablation_influence,
            "violation": detection.violation,
            "violation_types": detection.violation_types,
            "explanation": detection.explanation,
        }
        results.append(result_row)

    total = len(results)
    violations = sum(1 for r in results if r["violation"])
    compliant = total - violations

    outputs_dir = project_root / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    summary_json_path = outputs_dir / "mvp_summary.json"
    with summary_json_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "total_cases": total,
                "compliant_cases": compliant,
                "violating_cases": violations,
                "violation_counts": dict(violation_counter),
                "results": results,
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
        for row in results[:5]:
            f.write(f"- {row['case_id']}: violation={row['violation']} ")
            f.write(f"types={row['violation_types']} ")
            f.write(f"used={row['used_sources']}\n")
            f.write(f"  explanation: {row['explanation']}\n")

    print(f"Saved {summary_json_path}")
    print(f"Saved {summary_md_path}")
    print(f"Total={total}, Compliant={compliant}, Violating={violations}")


if __name__ == "__main__":
    main()
