import argparse
import shlex
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def run_command(cmd: list[str], dry_run: bool) -> None:
    print("$ " + " ".join(shlex.quote(part) for part in cmd))
    if dry_run:
        return
    subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)


def compare_mode(args: argparse.Namespace) -> None:
    python = sys.executable

    base_main = [
        python,
        "main.py",
        "--model",
        args.model,
        "--quantization",
        args.quantization,
        "--cases",
        args.run_a_cases,
        "--limit",
        str(args.limit),
        "--max-new-tokens",
        str(args.max_new_tokens),
    ]
    if args.skip_ablations:
        base_main.append("--skip-ablations")
    run_command(base_main, args.dry_run)

    archive_a = [
        python,
        "src/analysis/archive_run_outputs.py",
        "--run-name",
        args.run_a_name,
        "--case-file",
        args.run_a_cases,
        "--model",
        args.model,
        "--quantization",
        args.quantization,
        "--notes",
        args.notes_a,
    ]
    run_command(archive_a, args.dry_run)

    attack_main = [
        python,
        "main.py",
        "--model",
        args.model,
        "--quantization",
        args.quantization,
        "--cases",
        args.run_b_cases,
        "--limit",
        str(args.limit),
        "--max-new-tokens",
        str(args.max_new_tokens),
    ]
    if args.skip_ablations:
        attack_main.append("--skip-ablations")
    run_command(attack_main, args.dry_run)

    archive_b = [
        python,
        "src/analysis/archive_run_outputs.py",
        "--run-name",
        args.run_b_name,
        "--case-file",
        args.run_b_cases,
        "--model",
        args.model,
        "--quantization",
        args.quantization,
        "--notes",
        args.notes_b,
    ]
    run_command(archive_b, args.dry_run)

    metrics_json = f"outputs/analysis/{args.comparison_name}_metrics.json"
    table_md = f"outputs/analysis/{args.comparison_name}_table.md"

    collect = [
        python,
        "src/analysis/collect_comparison_metrics.py",
        "--run-dir",
        f"outputs/archive/{args.run_a_name}",
        "--run-dir",
        f"outputs/archive/{args.run_b_name}",
        "--write-output",
        metrics_json,
    ]
    run_command(collect, args.dry_run)

    render = [
        python,
        "src/analysis/render_mmmu_comparison_table.py",
        "--metrics-json",
        metrics_json,
        "--write-output",
        table_md,
        "--title",
        args.title or "Comparison Table",
    ]
    run_command(render, args.dry_run)

    if not args.dry_run:
        print(f"comparison metrics: {metrics_json}")
        print(f"comparison table: {table_md}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Top-level experiment runner for reproducible comparisons")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    compare = subparsers.add_parser("compare", help="Run, archive, and compare two experiment slices")
    compare.add_argument("--model", required=True, help="Model id to run through main.py")
    compare.add_argument("--quantization", default="none", help="Quantization mode passed to main.py")
    compare.add_argument("--run-a-name", required=True, help="Archive name for experiment A")
    compare.add_argument("--run-a-cases", required=True, help="Case file for experiment A")
    compare.add_argument("--run-b-name", required=True, help="Archive name for experiment B")
    compare.add_argument("--run-b-cases", required=True, help="Case file for experiment B")
    compare.add_argument("--limit", type=int, default=10, help="Case limit for both runs")
    compare.add_argument("--max-new-tokens", type=int, default=96, help="Generation budget for both runs")
    compare.add_argument("--comparison-name", required=True, help="Prefix for generated analysis artifacts")
    compare.add_argument("--title", default="", help="Optional markdown title for the rendered comparison table")
    compare.add_argument("--notes-a", default="", help="Archive note for experiment A")
    compare.add_argument("--notes-b", default="", help="Archive note for experiment B")
    compare.add_argument("--skip-ablations", action="store_true", help="Pass through to main.py")
    compare.add_argument("--dry-run", action="store_true", help="Print commands without executing them")
    compare.set_defaults(func=compare_mode)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
