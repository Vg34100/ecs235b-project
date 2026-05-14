import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


OUTPUT_FILES = [
    "policy_traces.json",
    "policy_traces.csv",
    "policy_trace_table.md",
    "evaluation_summary.md",
    "mvp_summary.json",
    "mvp_summary.md",
]


def copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        shutil.copy2(src, dst)


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive the current outputs/ directory under a stable run name")
    parser.add_argument("--run-name", required=True, help="Archive folder name, for example mmmu_base_10")
    parser.add_argument(
        "--source-dir",
        default="outputs",
        help="Directory containing the current run outputs",
    )
    parser.add_argument(
        "--archive-root",
        default="outputs/archive",
        help="Directory where named run archives should be stored",
    )
    parser.add_argument(
        "--case-file",
        default="",
        help="Optional case file used for the run; copied into the archive as case_snapshot.json",
    )
    parser.add_argument("--model", default="", help="Optional model id for the run manifest")
    parser.add_argument("--quantization", default="", help="Optional quantization setting for the run manifest")
    parser.add_argument("--notes", default="", help="Optional notes for the run manifest")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent
    source_dir = project_root / args.source_dir
    archive_dir = project_root / args.archive_root / args.run_name
    archive_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    for filename in OUTPUT_FILES:
        src = source_dir / filename
        dst = archive_dir / filename
        copy_if_exists(src, dst)
        if src.exists():
            copied.append(filename)

    case_snapshot_name = ""
    if args.case_file:
        case_src = project_root / args.case_file
        if case_src.exists():
            case_snapshot_name = "case_snapshot.json"
            shutil.copy2(case_src, archive_dir / case_snapshot_name)

    manifest = {
        "run_name": args.run_name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_dir": args.source_dir,
        "copied_files": copied,
        "case_file": args.case_file,
        "case_snapshot": case_snapshot_name,
        "model": args.model,
        "quantization": args.quantization,
        "notes": args.notes,
    }
    (archive_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"archived run to {display_path(archive_dir, project_root)}")
    print(f"copied files: {', '.join(copied) if copied else 'none'}")
    if case_snapshot_name:
        print(f"case snapshot: {case_snapshot_name}")


if __name__ == "__main__":
    main()
