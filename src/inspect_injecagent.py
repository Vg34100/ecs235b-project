import argparse
import json
from collections import Counter
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    # Keep this explicit so it is easy to reuse in the converter later.
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def short_text(value: str, limit: int = 110) -> str:
    # Just for readable terminal output.
    value = value.replace("\n", " ").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def print_counter(title: str, counter: Counter, top_k: int = 10) -> None:
    print(title)
    for key, value in counter.most_common(top_k):
        print(f"  {key}: {value}")
    print()


def summarize_user_cases(user_cases: list[dict]) -> None:
    # Tool/domain spread matters for choosing a good curated subset.
    tool_counter = Counter(case["User Tool"] for case in user_cases)
    level_counter = Counter(case["Level"] for case in user_cases)

    print(f"user cases: {len(user_cases)}")
    print_counter("top user tools", tool_counter)
    print_counter("difficulty levels", level_counter)


def summarize_attacker_cases(name: str, cases: list[dict]) -> None:
    # Attack-family spread matters for later policy templates.
    attack_type_counter = Counter(case["Attack Type"] for case in cases)
    tool_counter = Counter()
    for case in cases:
        for tool_name in case["Attacker Tools"]:
            tool_counter[tool_name] += 1

    print(f"{name}: {len(cases)}")
    print_counter(f"{name} attack types", attack_type_counter)
    print_counter(f"{name} attacker tools", tool_counter)


def summarize_test_cases(name: str, cases: list[dict]) -> None:
    # The synthesized files matter most because they are already combined cases.
    attack_type_counter = Counter(case["Attack Type"] for case in cases)
    user_tool_counter = Counter(case["User Tool"] for case in cases)

    print(f"{name}: {len(cases)}")
    print_counter(f"{name} attack types", attack_type_counter)
    print_counter(f"{name} user tools", user_tool_counter)


def print_sample_cases(name: str, cases: list[dict], limit: int) -> None:
    # Keep sample output simple so it is easy to sanity-check a subset.
    print(f"{name} sample cases")
    for index, case in enumerate(cases[:limit], start=1):
        print(f"  case {index}")
        print(f"    attack type: {case.get('Attack Type', 'n/a')}")
        print(f"    user tool: {case.get('User Tool', 'n/a')}")
        print(f"    attacker tools: {case.get('Attacker Tools', [])}")
        print(f"    user instruction: {short_text(case.get('User Instruction', ''))}")
        print(f"    attacker instruction: {short_text(case.get('Attacker Instruction', ''))}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect local InjecAgent benchmark files")
    parser.add_argument(
        "--root",
        default="data/raw/injecagent",
        help="Path to the local InjecAgent raw-data folder",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=3,
        help="How many sample synthesized cases to print per benchmark file",
    )
    args = parser.parse_args()

    # This is just for understanding the benchmark before conversion.
    root = Path(args.root)
    user_cases = load_jsonl(root / "user_cases.jsonl")
    attacker_dh = load_jsonl(root / "attacker_cases_dh.jsonl")
    attacker_ds = load_jsonl(root / "attacker_cases_ds.jsonl")
    test_dh_base = load_json(root / "test_cases_dh_base.json")
    test_ds_base = load_json(root / "test_cases_ds_base.json")

    print("InjecAgent local dataset inspection")
    print(f"root: {root.resolve()}")
    print()

    summarize_user_cases(user_cases)
    summarize_attacker_cases("attacker_cases_dh", attacker_dh)
    summarize_attacker_cases("attacker_cases_ds", attacker_ds)
    summarize_test_cases("test_cases_dh_base", test_dh_base)
    summarize_test_cases("test_cases_ds_base", test_ds_base)
    print_sample_cases("test_cases_dh_base", test_dh_base, args.samples)
    print_sample_cases("test_cases_ds_base", test_ds_base, args.samples)


if __name__ == "__main__":
    main()
