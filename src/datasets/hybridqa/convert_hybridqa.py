import argparse
import json
import re
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


def normalize_words(text: str) -> set[str]:
    stopwords = {
        "the",
        "a",
        "an",
        "of",
        "to",
        "and",
        "or",
        "in",
        "on",
        "for",
        "what",
        "which",
        "who",
        "when",
        "where",
        "was",
        "were",
        "did",
        "is",
        "are",
        "after",
    }
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {word for word in words if len(word) > 2 and word not in stopwords}


def cell_url_tokens(urls: list[str]) -> set[str]:
    tokens = set()
    for url in urls:
        tail = url.split("/")[-1].replace("_", " ")
        tokens |= normalize_words(tail)
    return tokens


def rank_rows_by_question_overlap(table: dict[str, Any], question: str) -> list[tuple[int, int]]:
    # We keep the raw row scores around so stricter selection rules can reject
    # cases where several rows look equally plausible.
    question_words = normalize_words(question)
    ranked = []
    for idx, row in enumerate(table.get("data", [])):
        cell_text = " ".join(cell[0] for cell in row)
        row_words = normalize_words(cell_text)
        row_words |= cell_url_tokens([url for cell in row for url in cell[1]])
        overlap = len(question_words & row_words)
        if overlap == 0:
            continue
        ranked.append((overlap, idx))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return ranked


def select_relevant_row_indices(table: dict[str, Any], question: str, row_limit: int = 4) -> list[int]:
    # The first rows in the raw table are often irrelevant. We rank rows by how
    # much they look like the question, then keep a small relevant slice.
    ranked = rank_rows_by_question_overlap(table, question)

    if not ranked:
        return list(range(min(row_limit, len(table.get("data", [])))))

    return [idx for _, idx in ranked[:row_limit]]


def compact_rows(table: dict[str, Any], row_indices: list[int]) -> list[list[str]]:
    # Keep only the rows we think matter to the question, in relevance order.
    rows = []
    data = table.get("data", [])
    for idx in row_indices:
        if 0 <= idx < len(data):
            rows.append([cell[0] for cell in data[idx]])
    return rows


def collect_linked_text(
    table: dict[str, Any],
    request: dict[str, str],
    row_indices: list[int],
    summary_limit: int = 4,
) -> list[dict[str, str]]:
    # Pull linked summaries from the rows we selected first, then fall back if
    # those rows do not give us enough text evidence.
    linked = []
    seen = set()
    data = table.get("data", [])

    def maybe_add_from_row(row: list[Any]) -> bool:
        nonlocal linked
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
                    return True
        return False

    for idx in row_indices:
        if 0 <= idx < len(data) and maybe_add_from_row(data[idx]):
            return linked

    for idx, row in enumerate(data):
        if idx in row_indices:
            continue
        if maybe_add_from_row(row):
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


def answer_appears_in_table(table: dict[str, Any], answer: str) -> bool:
    answer_low = answer.lower().strip()
    if not answer_low:
        return False
    for row in table.get("data", []):
        for cell_text, _ in row:
            if answer_low in cell_text.lower():
                return True
    return False


def question_is_strict_friendly(question: str) -> bool:
    question_low = question.lower().strip()
    blocked_phrases = [
        "difference",
        "how many",
        "later played for",
        "what kind of",
        "what type of",
        "how long",
        "what is the time",
        "how much more",
        "how much less",
    ]
    if any(phrase in question_low for phrase in blocked_phrases):
        return False
    return True


def answer_is_strict_friendly(answer: str) -> bool:
    answer = answer.strip()
    if not answer or len(answer) > 40:
        return False
    if "," in answer or ";" in answer:
        return False
    if " and " in answer.lower():
        return False
    if re.fullmatch(r"\d{1,4}", answer):
        return True
    if re.fullmatch(r"\$?\s?\d[\d,]*(\.\d+)?", answer):
        return True
    word_count = len(answer.split())
    return 1 <= word_count <= 4


def linked_text_is_strict_friendly(linked_text: list[dict[str, str]], answer: str) -> bool:
    answer_low = answer.lower().strip()
    if not answer_low:
        return False
    for item in linked_text:
        summary = item["summary"]
        if len(summary) > 900:
            continue
        if answer_low in summary.lower():
            return True
    return False


def top_row_is_clear_match(ranked_rows: list[tuple[int, int]]) -> bool:
    if not ranked_rows:
        return False
    top_score = ranked_rows[0][0]
    if top_score < 2:
        return False
    if len(ranked_rows) == 1:
        return True
    second_score = ranked_rows[1][0]
    return top_score > second_score


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


def is_good_strict_case(
    example: dict[str, Any],
    table: dict[str, Any],
    linked_text: list[dict[str, str]],
    ranked_rows: list[tuple[int, int]],
    required_sources: list[str],
) -> bool:
    # The stricter selector is for scale-up, so it rejects ambiguous or messy
    # cases instead of trying to rescue them with detector tweaks later.
    if not is_good_pilot_case(example, table, linked_text):
        return False

    question = example.get("question", "").strip()
    answer = example.get("answer-text", "").strip()
    if not question_is_strict_friendly(question):
        return False
    if not answer_is_strict_friendly(answer):
        return False
    if not top_row_is_clear_match(ranked_rows):
        return False

    if "linked_text" in required_sources:
        if answer_appears_in_table(table, answer):
            return False
        if not linked_text_is_strict_friendly(linked_text, answer):
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


def strict_score_case(
    example: dict[str, Any],
    table: dict[str, Any],
    linked_text: list[dict[str, str]],
    ranked_rows: list[tuple[int, int]],
    required_sources: list[str],
) -> int:
    # This score prefers cases that keep the answer target compact and the row
    # selection story obvious.
    score = score_case(example, table, linked_text)
    answer = example.get("answer-text", "").strip()
    if answer_is_strict_friendly(answer):
        score += 3
    if top_row_is_clear_match(ranked_rows):
        score += 3
    if "linked_text" in required_sources and linked_text_is_strict_friendly(linked_text, answer):
        score += 3
    if "linked_text" in required_sources and answer_appears_in_table(table, answer):
        score -= 5
    return score


def case_bucket(required_sources: list[str]) -> str:
    # HybridQA is table-anchored, so the useful split here is whether linked
    # text is also required, not whether the case is somehow text-only.
    if "linked_text" in required_sources:
        return "table_plus_text"
    return "table_only"


def load_existing_cases(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def convert_example(example: dict[str, Any], table: dict[str, Any], request: dict[str, str]) -> dict[str, Any]:
    row_indices = select_relevant_row_indices(table, example["question"])
    linked_text = collect_linked_text(table, request, row_indices)
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
                "rows": compact_rows(table, row_indices),
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
    parser.add_argument(
        "--selector",
        choices=["broad", "strict"],
        default="broad",
        help="Selection rule set for automatic subset generation",
    )
    parser.add_argument(
        "--extend-from",
        default="",
        help="Existing converted case file to preserve and extend",
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
    preserved_by_id = {}
    preserved_bucket_counts = {"table_only": 0, "table_plus_text": 0}

    if args.extend_from:
        extend_path = project_root / args.extend_from
        for case in load_existing_cases(extend_path):
            preserved_by_id[case["case_id"]] = case
            bucket = case_bucket(case["required_sources"])
            preserved_bucket_counts[bucket] += 1
        converted.extend(preserved_by_id.values())

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

                row_indices = select_relevant_row_indices(table, example["question"])
                linked_text = collect_linked_text(table, request, row_indices)
                if not is_good_pilot_case(example, table, linked_text):
                    continue

                converted.append(convert_example(example, table, request))
        else:
            ranked_by_bucket = {"table_only": [], "table_plus_text": []}
            for example in examples:
                case_id = f"hybridqa_{example['question_id']}"
                if case_id in preserved_by_id:
                    continue
                try:
                    table, request = load_table_bundle(archive, example["table_id"])
                except KeyError:
                    continue

                ranked_rows = rank_rows_by_question_overlap(table, example["question"])
                row_indices = select_relevant_row_indices(table, example["question"])
                linked_text = collect_linked_text(table, request, row_indices)
                if not is_good_pilot_case(example, table, linked_text):
                    continue

                required_sources = infer_required_sources(
                    example["question"], example.get("answer-text", ""), linked_text
                )
                if args.selector == "strict" and not is_good_strict_case(
                    example, table, linked_text, ranked_rows, required_sources
                ):
                    continue
                bucket = case_bucket(required_sources)
                if args.selector == "strict":
                    score = strict_score_case(example, table, linked_text, ranked_rows, required_sources)
                else:
                    score = score_case(example, table, linked_text)

                ranked_by_bucket[bucket].append(
                    (score, example["question_id"], example, table, request)
                )

            for bucket_items in ranked_by_bucket.values():
                bucket_items.sort(key=lambda item: (-item[0], item[1]))

            chosen = []
            table_only_needed = max(0, args.table_only_limit - preserved_bucket_counts["table_only"])
            table_plus_text_needed = max(
                0, args.table_plus_text_limit - preserved_bucket_counts["table_plus_text"]
            )
            chosen.extend(ranked_by_bucket["table_only"][:table_only_needed])
            chosen.extend(ranked_by_bucket["table_plus_text"][:table_plus_text_needed])

            # If one bucket comes up short, backfill from the other bucket so
            # the converter still returns a usable subset.
            if len(converted) + len(chosen) < args.limit:
                used_ids = {item[1] for item in chosen} | {
                    case_id.removeprefix("hybridqa_") for case_id in preserved_by_id
                }
                leftovers = []
                for bucket_name in ("table_only", "table_plus_text"):
                    for item in ranked_by_bucket[bucket_name]:
                        if item[1] in used_ids:
                            continue
                        leftovers.append(item)
                leftovers.sort(key=lambda item: (-item[0], item[1]))
                chosen.extend(leftovers[: max(0, args.limit - (len(converted) + len(chosen)))])

            chosen.sort(key=lambda item: item[1])
            for _, _, example, table, request in chosen[: max(0, args.limit - len(converted))]:
                converted.append(convert_example(example, table, request))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2)

    print(f"wrote {output_path.relative_to(project_root)}")
    if args.selected_ids:
        print(f"selection mode: selected_ids")
        print(f"selected ids requested: {len(selected_ids)}")
    else:
        print(f"selection mode: {args.selector}")
        print(f"target limit: {args.limit}")
        print(f"table_only target: {args.table_only_limit}")
        print(f"table_plus_text target: {args.table_plus_text_limit}")
        if args.extend_from:
            print(f"extended from: {args.extend_from}")
    print(f"pilot cases: {len(converted)}")
    if converted:
        first = converted[0]
        print(f"sample case: {first['case_id']}")
        print(f"required sources: {first['required_sources']}")


if __name__ == "__main__":
    main()
