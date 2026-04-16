from dataclasses import dataclass


@dataclass
class FlowPolicy:
    case_id: str
    required_sources: list[str]
    forbidden_sources: list[str]


@dataclass
class PolicyResult:
    is_compliant: bool
    violation_types: list[str]
    explanation: str


def evaluate_policy(policy: FlowPolicy, used_sources: list[str]) -> PolicyResult:
    used = set(used_sources)
    required = set(policy.required_sources)
    forbidden = set(policy.forbidden_sources)

    missing_required = sorted(required - used)
    used_forbidden = sorted(forbidden & used)

    violations: list[str] = []
    reasons: list[str] = []

    if missing_required:
        violations.append("missing_required_source")
        reasons.append(f"missing required sources: {', '.join(missing_required)}")

    if used_forbidden:
        violations.append("forbidden_source_used")
        reasons.append(f"used forbidden sources: {', '.join(used_forbidden)}")

    if not violations:
        return PolicyResult(
            is_compliant=True,
            violation_types=[],
            explanation="policy compliant",
        )

    return PolicyResult(
        is_compliant=False,
        violation_types=violations,
        explanation="; ".join(reasons),
    )
