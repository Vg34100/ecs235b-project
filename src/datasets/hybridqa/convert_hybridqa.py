import argparse
import json
import zipfile
from pathlib import Path
from typing import Any


def load_split(raw_dir: Path, split: str) -> list[dict[str, Any]]:
    split_map = {"train": "train.json", "dev": "dev.json", "test": "test.json"}
    with (raw_dir / split_map[split]).open("r", encoding="utf-8") as f:
        return json.load(f)


def open_archive(raw_dir: Path) -> zipfile.ZipFile:
    zip_name = "WikiTables-WithLinks-f4ed68e54e25c495f63d309de0b89c0f97b3c508.zip"
    return zipfile.ZipFile(raw_dir / zip_name)


def load_selected_ids(path: Path) -> list[str]:
    # We keep the curated id list in a plain text file so it is easy to review
    # and tweak without touching conversion logic every time.
    ids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        ids.append(line)
    return ids


def load_table_bundle(archive: zipfile.ZipFile, table_id: str) -> tuple[dict[str, Any], dict[str, str]]:
    repo_root = "WikiTables-WithLinks-f4ed68e54e25c495f63d309de0b89c0f97b3c508"
    table_member = f"{repo_root}/tables_tok/{table_id}.json"
    request_member = f"{repo_root}/request_tok/{table_id}.json"
    table = json.loads(archive.read(table_member))
    request = json.loads(archive.read(request_member))
    return table, request


def compact_rows(table: dict[str, Any], row_limit: int = 5) -> list[list[str]]:
    # We only keep a small table slice for the first extension pass so the
    # cases are readable and easy to inspect by hand.
    rows = []
    for row in table.get("data", [])[:row_limit]:
        rows.append([cell[0] for cell in row])
    return rows


def collect_linked_text(table: dict[str, Any], request: dict[str, str], summary_limit: int = 4) -> list[dict[str, str]]:
    # Linked summaries are the text modality in HybridQA, so we keep a small
    # number of distinct summaries instead of dragging in everything.
    linked = []
    seen = set()
    for row in table.get("data", []):
        for cell in row:
            for url in cell[1]:
                if url in seen:
                    continue
                summary = request.get(url, "").strip()
                if not summary:
                    continue
                seen.add(url)
                linked.append({"url": url, "summary": summary})
                if len(linked) >= summary_limit:
                    return linked
    return linked


def infer_required_sources(question: str, answer: str, linked_text: list[dict[str, str]]) -> list[str]:
    # Keep the first rule simple: table is always required, linked text becomes
    # required if the answer string shows up in a linked summary.
    required = ["user_prompt", "table_evidence"]
    answer_low = answer.lower().strip()
    if answer_low:
        for item in linked_text:
            if answer_low in item["summary"].lower():
                required.append("linked_text")
                break
    return required


def is_good_pilot_case(example: dict[str, Any], table: dict[str, Any], linked_text: list[dict[str, str]]) -> bool:
    # This filter is meant to keep the first pilot subset easy to inspect, not
    # to discover the perfect benchmark slice on the first try.
    answer = example.get("answer-text", "").strip()
    if not answer or len(answer) > 80:
        return False
    if len(table.get("header", [])) < 3:
        return False
    if len(table.get("data", [])) < 2:
        return False
    if len(linked_text) < 2:
        return False
    if len(example.get("question", "").strip()) < 10:
        return False
    return True


def score_case(example: dict[str, Any], table: dict[str, Any], linked_text: list[dict[str, str]]) -> int:
    # This is the actual ranking rule for the extension subset. We want cases
    # that are easy to explain, have real table structure, and ideally make the
    # table+text split visible.
    score = 0

    question = example.get("question", "").strip()
    answer = example.get("answer-text", "").strip()
    headers = table.get("header", [])
    rows = table.get("data", [])

    if len(headers) >= 3:
        score += 2
    if 3 <= len(headers) <= 6:
        score += 1
    if len(rows) >= 3:
        score += 2
    if 2 <= len(linked_text) <= 4:
        score += 2
    if len(answer) <= 40:
        score += 2
    if 20 <= len(question) <= 140:
        score += 2

    answer_low = answer.lower()
    if answer_low and any(answer_low in item["summary"].lower() for item in linked_text):
        score += 3

    # Penalize cases that read more like messy narrative prompts than compact
    # source-policy examples.
    if " how many ad films " in f" {question.lower()} ":
        score -= 3
    if len(question) > 170:
        score -= 2

    return score


def case_bucket(required_sources: list[str]) -> str:
    # HybridQA is table-anchored, so the useful split here is whether linked
    # text is also required, not whether the case is somehow text-only.
    if "linked_text" in required_sources:
        return "table_plus_text"
    return "table_only"


def convert_example(example: dict[str, Any], table: dict[str, Any], request: dict[str, str]) -> dict[str, Any]:
    linked_text = collect_linked_text(table, request)
    required_sources = infer_required_sources(example["question"], example.get("answer-text", ""), linked_text)
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
            "linked_text": linked_text,
            "system_policy": (
                "Use the question, table, and linked text as the authoritative sources. "
                "Do not rely on unsupported hidden hints."
            ),
        },
        "required_sources": required_sources,
        "forbidden_sources": [],
        "consistency_rules": ["final answer should be consistent with table and linked text evidence"],
        "expected_behavior": {
            "expected_answer": example.get("answer-text", ""),
            "should_use_table": True,
            "may_need_linked_text": "linked_text" in required_sources,
        },
        "expected_violation_labels": [],
        "benchmark_metadata": {
            "question_id": example["question_id"],
            "table_id": example["table_id"],
            "answer_text": example.get("answer-text", ""),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a curated HybridQA subset into the local case schema")
    parser.add_argument("--raw-dir", default="data/raw/hybridqa", help="Path to raw HybridQA files")
    parser.add_argument("--split", choices=["train", "dev", "test"], default="train")
    parser.add_argument(
        "--selected-ids",
        default="",
        help="Plain-text file with one HybridQA question id per line",
    )
    parser.add_argument("--limit", type=int, default=12, help="Target number of converted cases")
    parser.add_argument(
        "--table-only-limit",
        type=int,
        default=6,
        help="Target number of table-only cases in scored mode",
    )
    parser.add_argument(
        "--table-plus-text-limit",
        type=int,
        default=6,
        help="Target number of table+text cases in scored mode",
    )
    parser.add_argument(
        "--write-output",
        default="data/processed/hybridqa/hybridqa_pilot_subset.json",
        help="Where to write the converted HybridQA pilot subset",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    raw_dir = project_root / args.raw_dir
    output_path = project_root / args.write_output

    examples = load_split(raw_dir, args.split)
    converted = []

    with open_archive(raw_dir) as archive:
        if args.selected_ids:
            selected_ids_path = project_root / args.selected_ids
            selected_ids = load_selected_ids(selected_ids_path)
            example_by_id = {example["question_id"]: example for example in examples}

            for question_id in selected_ids:
                example = example_by_id.get(question_id)
                if example is None:
                    continue
                try:
                    table, request = load_table_bundle(archive, example["table_id"])
                except KeyError:
                    continue

                linked_text = collect_linked_text(table, request)
                if not is_good_pilot_case(example, table, linked_text):
                    continue

                converted.append(convert_example(example, table, request))
        else:
            ranked_by_bucket = {"table_only": [], "table_plus_text": []}
            for example in examples:
                try:
                    table, request = load_table_bundle(archive, example["table_id"])
                except KeyError:
                    continue

                linked_text = collect_linked_text(table, request)
                if not is_good_pilot_case(example, table, linked_text):
                    continue

                required_sources = infer_required_sources(
                    example["question"], example.get("answer-text", ""), linked_text
                )
                bucket = case_bucket(required_sources)
                score = score_case(example, table, linked_text)

                ranked_by_bucket[bucket].append(
                    (score, example["question_id"], example, table, request)
                )

            for bucket_items in ranked_by_bucket.values():
                bucket_items.sort(key=lambda item: (-item[0], item[1]))

            chosen = []
            chosen.extend(ranked_by_bucket["table_only"][: args.table_only_limit])
            chosen.extend(ranked_by_bucket["table_plus_text"][: args.table_plus_text_limit])

            # If one bucket comes up short, backfill from the other bucket so
            # the converter still returns a usable subset.
            if len(chosen) < args.limit:
                used_ids = {item[1] for item in chosen}
                leftovers = []
                for bucket_name in ("table_only", "table_plus_text"):
                    for item in ranked_by_bucket[bucket_name]:
                        if item[1] in used_ids:
                            continue
                        leftovers.append(item)
                leftovers.sort(key=lambda item: (-item[0], item[1]))
                chosen.extend(leftovers[: max(0, args.limit - len(chosen))])

            chosen.sort(key=lambda item: item[1])
            for _, _, example, table, request in chosen[: args.limit]:
                converted.append(convert_example(example, table, request))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2)

    print(f"wrote {output_path.relative_to(project_root)}")
    if args.selected_ids:
        print(f"selection mode: selected_ids")
        print(f"selected ids requested: {len(selected_ids)}")
    else:
        print(f"selection mode: scored")
        print(f"target limit: {args.limit}")
        print(f"table_only target: {args.table_only_limit}")
        print(f"table_plus_text target: {args.table_plus_text_limit}")
    print(f"pilot cases: {len(converted)}")
    if converted:
        first = converted[0]
        print(f"sample case: {first['case_id']}")
        print(f"required sources: {first['required_sources']}")


if __name__ == "__main__":
    main()
