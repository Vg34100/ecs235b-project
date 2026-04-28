from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class PolicyTrace:
    # This is the main record we want to carry into evaluation and reporting.
    case_id: str
    model_name: str
    prompt: str
    available_sources: list[str]
    required_sources: list[str]
    forbidden_sources: list[str]
    model_answer: str
    used_sources_reported: list[str]
    used_sources_inferred: list[str]
    final_used_sources: list[str]
    violation: bool
    violation_types: list[str]
    policy_explanation: str
    ablation_influence: dict[str, bool]
    raw_output: str
    run_reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_primary_prompt_source(case: dict[str, Any]) -> str:
    if "sources" in case:
        return "user_prompt"
    return "prompt"


def get_case_prompt(case: dict[str, Any]) -> str:
    if "prompt" in case:
        return str(case["prompt"])
    if "sources" in case:
        return str(case["sources"].get("user_prompt", ""))
    return ""


def get_available_sources(case: dict[str, Any]) -> list[str]:
    if "sources" in case:
        return sorted(case["sources"].keys())
    return ["prompt", "image_evidence", "retrieved_context", "hidden_metadata"]
