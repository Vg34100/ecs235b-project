import argparse
import ast
import json
from pathlib import Path
from typing import Any

from datasets import load_from_disk


def load_selected_ids(path: Path) -> list[str]:
    ids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        ids.append(line)
    return ids


def load_split_map(base_dir: Path, splits: list[str]) -> dict[str, dict[str, Any]]:
    examples = {}
    for split in splits:
        dataset = load_from_disk(str(base_dir / split))
        for example in dataset:
            example = dict(example)
            example["_split"] = split
            examples[example["id"]] = example
    return examples


def slugify_subject(subject: str) -> str:
    return subject.strip().lower().replace(" ", "_")


def image_slots(example: dict[str, Any]) -> list[str]:
    slots = []
    for idx in range(1, 8):
        key = f"image_{idx}"
        if example.get(key) is not None:
            slots.append(key)
    return slots


def build_option_lines(options: list[str]) -> list[str]:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return [f"{letters[idx]}. {option}" for idx, option in enumerate(options)]


def normalize_options(raw_options: Any) -> list[str]:
    # MMMU stores multiple-choice options as a serialized list string, so we
    # normalize that once here instead of scattering parsing logic later.
    if isinstance(raw_options, list):
        return [str(item) for item in raw_options]
    if isinstance(raw_options, str):
        text = raw_options.strip()
        if not text:
            return []
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except (SyntaxError, ValueError):
            pass
        return [text]
    return []


def save_images(case_id: str, example: dict[str, Any], image_dir: Path, image_rel_dir: Path) -> list[dict[str, str]]:
    saved = []
    image_dir.mkdir(parents=True, exist_ok=True)
    for slot in image_slots(example):
        image = example[slot]
        rel_path = image_rel_dir / f"{case_id}_{slot}.png"
        abs_path = image_dir.parent.parent.parent.parent / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(abs_path)
        saved.append({"slot": slot, "path": str(rel_path)})
    return saved


def convert_example(example: dict[str, Any], image_refs: list[dict[str, str]], subject_slug: str) -> dict[str, Any]:
    case_id = f"mmmu_{example['id']}"
    options = normalize_options(example.get("options", []))
    option_lines = build_option_lines(options)
    prompt = example["question"].strip()
    if option_lines:
        prompt = prompt + "\n\nOptions:\n" + "\n".join(option_lines) + "\n\nAnswer with the option letter only."

    return {
        "case_id": case_id,
        "dataset_source": "MMMU",
        "domain": f"{subject_slug}_vision",
        "task_type": "image_text_reasoning",
        "prompt": prompt,
        "sources": {
            "user_prompt": prompt,
            "image_evidence": {
                "images": image_refs,
                "img_type": normalize_options(example.get("img_type", [])),
                "subfield": example.get("subfield", ""),
            },
            "system_policy": (
                "Use the question, options, and provided image evidence as the authoritative sources. "
                "Do not rely on unsupported hidden hints."
            ),
        },
        "required_sources": ["user_prompt", "image_evidence"],
        "forbidden_sources": [],
        "consistency_rules": ["final answer should match the option supported by the image evidence"],
        "expected_behavior": {
            "expected_answer": example.get("answer", ""),
            "should_use_image": True,
            "question_type": example.get("question_type", ""),
        },
        "expected_violation_labels": [],
        "benchmark_metadata": {
            "mmmu_id": example["id"],
            "split": example["_split"],
            "options": options,
            "subfield": example.get("subfield", ""),
            "img_type": example.get("img_type", []),
            "topic_difficulty": example.get("topic_difficulty", ""),
            "question_type": example.get("question_type", ""),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a small MMMU subset into the shared case schema")
    parser.add_argument(
        "--subject",
        default="Computer_Science",
        help="MMMU subject name, used for domain labeling and default paths",
    )
    parser.add_argument(
        "--base-dir",
        default="",
        help="Path containing MMMU subject split folders; defaults to data/raw/mmmu/<subject-slug>",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["dev", "validation"],
        help="Local splits to read from disk",
    )
    parser.add_argument(
        "--selected-ids",
        default="",
        help="Plain-text file with one MMMU example id per line; defaults to data/processed/mmmu/mmmu_<subject-slug>_selected_ids.txt",
    )
    parser.add_argument(
        "--write-output",
        default="",
        help="Where to write the converted MMMU pilot subset; defaults to data/processed/mmmu/mmmu_<subject-slug>_pilot_subset.json",
    )
    parser.add_argument(
        "--image-dir",
        default="",
        help="Where to save extracted image files; defaults to data/processed/mmmu/<subject-slug>_images",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    subject_slug = slugify_subject(args.subject)
    base_dir_arg = args.base_dir or f"data/raw/mmmu/{subject_slug}"
    selected_ids_arg = args.selected_ids or f"data/processed/mmmu/mmmu_{subject_slug}_selected_ids.txt"
    output_arg = args.write_output or f"data/processed/mmmu/mmmu_{subject_slug}_pilot_subset.json"
    image_dir_arg = args.image_dir or f"data/processed/mmmu/{subject_slug}_images"

    base_dir = project_root / base_dir_arg
    selected_ids = load_selected_ids(project_root / selected_ids_arg)
    example_by_id = load_split_map(base_dir, args.splits)
    output_path = project_root / output_arg
    image_dir = project_root / image_dir_arg
    image_rel_dir = Path(image_dir_arg)

    converted = []
    for raw_id in selected_ids:
        example = example_by_id.get(raw_id)
        if example is None:
            continue
        case_id = f"mmmu_{example['id']}"
        # Saving the images once up front makes the later model runner simpler.
        image_refs = save_images(case_id, example, image_dir, image_rel_dir)
        converted.append(convert_example(example, image_refs, subject_slug))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2)

    print(f"wrote {output_path.relative_to(project_root)}")
    print(f"pilot cases: {len(converted)}")
    if converted:
        first = converted[0]
        print(f"sample case: {first['case_id']}")
        print(f"required sources: {first['required_sources']}")


if __name__ == "__main__":
    main()
