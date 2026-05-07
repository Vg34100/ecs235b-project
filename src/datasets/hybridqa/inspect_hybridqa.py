import argparse
import json
import zipfile
from pathlib import Path
from typing import Any


def load_split(raw_dir: Path, split: str) -> list[dict[str, Any]]:
    # Keep split handling explicit so it is easy to swap train/dev/test while
    # we are still figuring out what a good extension subset looks like.
    split_map = {"train": "train.json", "dev": "dev.json", "test": "test.json"}
    path = raw_dir / split_map[split]
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def open_archive(raw_dir: Path) -> zipfile.ZipFile:
    zip_name = "WikiTables-WithLinks-f4ed68e54e25c495f63d309de0b89c0f97b3c508.zip"
    return zipfile.ZipFile(raw_dir / zip_name)


def load_table_bundle(archive: zipfile.ZipFile, table_id: str) -> tuple[dict[str, Any], dict[str, str]]:
    # The split JSON points to a table id; the real table and linked summaries
    # live inside the archive, so we pull both at the same time here.
    repo_root = "WikiTables-WithLinks-f4ed68e54e25c495f63d309de0b89c0f97b3c508"
    table_member = f"{repo_root}/tables_tok/{table_id}.json"
    request_member = f"{repo_root}/request_tok/{table_id}.json"
    table = json.loads(archive.read(table_member))
    request = json.loads(archive.read(request_member))
    return table, request


def compact_rows(table: dict[str, Any], row_limit: int = 5) -> list[list[str]]:
    # For prompting and inspection we do not want the whole raw table at first.
    # A small compact slice is easier to read and enough for a preview subset.
    rows = []
    for row in table.get("data", [])[:row_limit]:
        rows.append([cell[0] for cell in row])
    return rows


def collect_linked_text(table: dict[str, Any], request: dict[str, str], summary_limit: int = 4) -> list[dict[str, str]]:
    # Linked summaries are the text side of the table+text setup, so we keep a
    # small number of distinct summaries for the first conversion pass.
    linked = []
    seen = set()
    for row in table.get("data", []):
        for cell in row:
            for url in cell[1]:
                if url in seen:
                    continue
                seen.add(url)
                linked.append({"url": url, "summary": request.get(url, "")})
                if len(linked) >= summary_limit:
                    return linked
    return linked


def convert_example(example: dict[str, Any], table: dict[str, Any], request: dict[str, str]) -> dict[str, Any]:
    # This is only a first-pass mapping. We keep it compact on purpose so it is
    # easy to inspect and later refine into stronger policy cases.
    return {
        "case_id": f"hybridqa_{example['question_id']}",
        "dataset_source": "HybridQA",
        "domain": "tabular_reasoning",
        "task_type": "table_text_reasoning",
        "prompt": example["question"],
        "sources": {
            "user_prompt": example["question"],
            "table_evidence": {
                "title": table.get("title", ""),
                "url": table.get("url", ""),
                "header": [header[0] for header in table.get("header", [])],
                "rows": compact_rows(table),
            },
            "linked_text": collect_linked_text(table, request),
            "system_policy": (
                "Use the question, table, and linked text as the only authoritative sources. "
                "Do not rely on unsupported hidden hints."
            ),
        },
        "required_sources": ["user_prompt", "table_evidence"],
        "forbidden_sources": [],
        "consistency_rules": ["final answer should be consistent with table and linked text evidence"],
        "expected_behavior": {
            "expected_answer": example.get("answer-text", ""),
            "should_use_table": True,
            "may_need_linked_text": True,
        },
        "expected_violation_labels": [],
        "benchmark_metadata": {
            "table_id": example["table_id"],
            "answer_text": example.get("answer-text", ""),
        },
    }


def print_sample(example: dict[str, Any], table: dict[str, Any], request: dict[str, str]) -> None:
    # Print a readable preview first so we can decide whether the converted
    # subset is worth keeping before building a larger extension set.
    print(f"question_id: {example['question_id']}")
    print(f"question: {example['question']}")
    print(f"table_id: {example['table_id']}")
    print(f"answer_text: {example.get('answer-text', '')}")
    print(f"table_title: {table.get('title', '')}")
    print(f"header: {[header[0] for header in table.get('header', [])[:6]]}")
    rows = compact_rows(table, row_limit=2)
    for i, row in enumerate(rows, start=1):
        print(f"row_{i}: {row}")
    linked = collect_linked_text(table, request, summary_limit=2)
    for i, item in enumerate(linked, start=1):
        summary = item['summary'][:180].replace("\n", " ")
        print(f"linked_{i}: {item['url']} :: {summary}")
    print("-" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect and preview-convert a small HybridQA subset")
    parser.add_argument("--raw-dir", default="data/raw/hybridqa", help="Path to raw HybridQA files")
    parser.add_argument("--split", choices=["train", "dev", "test"], default="train")
    parser.add_argument("--limit", type=int, default=3, help="Number of examples to inspect/convert")
    parser.add_argument(
        "--write-preview",
        default="data/processed/hybridqa/hybridqa_preview.json",
        help="Where to write a small converted preview subset",
    )
    args = parser.parse_args()

    # This script now lives under src/datasets/hybridqa/, so we walk back up to
    # the project root before resolving data paths.
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    raw_dir = project_root / args.raw_dir
    preview_path = project_root / args.write_preview

    examples = load_split(raw_dir, args.split)[: args.limit]
    converted = []

    with open_archive(raw_dir) as archive:
        for example in examples:
            table, request = load_table_bundle(archive, example["table_id"])
            print_sample(example, table, request)
            converted.append(convert_example(example, table, request))

    preview_path.parent.mkdir(parents=True, exist_ok=True)
    with preview_path.open("w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2)

    print(f"Saved preview subset to {preview_path}")


if __name__ == "__main__":
    main()
