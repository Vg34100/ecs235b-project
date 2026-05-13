import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from datasets import load_from_disk


def image_slots(example: dict[str, Any]) -> list[str]:
    # Most Computer_Science MMMU items only use image_1, but we keep the helper
    # generic so later subjects with more image slots still inspect cleanly.
    slots = []
    for idx in range(1, 8):
        key = f"image_{idx}"
        if example.get(key) is not None:
            slots.append(key)
    return slots


def normalize_img_type(value: Any) -> tuple[str, ...]:
    if isinstance(value, list):
        return tuple(value)
    if value is None:
        return tuple()
    return (str(value),)


def print_summary(split: str, dataset: Any) -> None:
    print(f"SPLIT {split}: {len(dataset)} examples")
    print("columns:", dataset.column_names)
    print("img_type counts:", Counter(normalize_img_type(x) for x in dataset["img_type"]))
    print("question_type counts:", Counter(dataset["question_type"]))
    print("subfield counts:", Counter(dataset["subfield"]).most_common())
    print("difficulty counts:", Counter(dataset["topic_difficulty"]))
    print()


def print_examples(split: str, dataset: Any, limit: int) -> None:
    print(f"===== {split} examples =====")
    for idx in range(min(limit, len(dataset))):
        ex = dataset[idx]
        print("id:", ex["id"])
        print("subfield:", ex["subfield"])
        print("img_type:", ex["img_type"])
        print("question_type:", ex["question_type"])
        print("difficulty:", ex["topic_difficulty"])
        print("answer:", ex["answer"])
        print("question:", ex["question"].replace("\n", " "))
        print("options:", ex["options"])
        print("images_present:", image_slots(ex))
        print("---")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect local MMMU subject splits")
    parser.add_argument(
        "--base-dir",
        default="data/raw/mmmu/computer_science",
        help="Path containing MMMU split folders saved with datasets.save_to_disk",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["dev", "validation"],
        help="Splits to inspect",
    )
    parser.add_argument("--example-limit", type=int, default=8, help="How many examples to print per split")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    base_dir = project_root / args.base_dir

    for split in args.splits:
        dataset = load_from_disk(str(base_dir / split))
        print_summary(split, dataset)
        print_examples(split, dataset, args.example_limit)


if __name__ == "__main__":
    main()
