from dataclasses import dataclass
from typing import Any

from src.policies import FlowPolicy, evaluate_policy


@dataclass
class DetectionResult:
    case_id: str
    violation: bool
    violation_types: list[str]
    explanation: str
    used_sources: list[str]
    answer: str


def detect_case(case: dict[str, Any], used_sources: list[str], answer: str) -> DetectionResult:
    policy = FlowPolicy(
        case_id=case["case_id"],
        required_sources=case.get("required_sources", []),
        forbidden_sources=case.get("forbidden_sources", []),
    )

    result = evaluate_policy(policy, used_sources)

    return DetectionResult(
        case_id=case["case_id"],
        violation=not result.is_compliant,
        violation_types=result.violation_types,
        explanation=result.explanation,
        used_sources=used_sources,
        answer=answer,
    )
