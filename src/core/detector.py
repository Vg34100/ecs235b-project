from dataclasses import dataclass
from typing import Any

from src.core.policies import FlowPolicy, evaluate_policy


@dataclass
class DetectionResult:
    # Final policy judgment for one run of one case.
    case_id: str
    violation: bool
    violation_types: list[str]
    explanation: str
    used_sources: list[str]
    answer: str


def detect_case(case: dict[str, Any], used_sources: list[str], answer: str) -> DetectionResult:
    # Keep the detector thin; policy logic lives in policies.py.
    policy = FlowPolicy(
        case_id=case["case_id"],
        required_sources=case.get("required_sources", []),
        forbidden_sources=case.get("forbidden_sources", []),
        consistency_rules=case.get("consistency_rules", []),
        attacker_instruction=case.get("sources", {}).get("attacker_instruction", ""),
        expected_behavior=case.get("expected_behavior", {}),
    )

    result = evaluate_policy(policy, used_sources, answer)

    return DetectionResult(
        case_id=case["case_id"],
        violation=not result.is_compliant,
        violation_types=result.violation_types,
        explanation=result.explanation,
        used_sources=used_sources,
        answer=answer,
    )
