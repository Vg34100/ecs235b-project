from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class AccessControlMatrix:
    """Simple ACM for tracking read/write/influence rights."""

    matrix: Dict[str, Dict[str, Set[str]]] = field(default_factory=dict)

    def grant(self, subject: str, obj: str, right: str) -> None:
        self.matrix.setdefault(subject, {}).setdefault(obj, set()).add(right)

    def has_right(self, subject: str, obj: str, right: str) -> bool:
        return right in self.matrix.get(subject, {}).get(obj, set())

    def from_case_defaults(self, subject: str, sources: list[str]) -> None:
        """Give one subject read rights to listed sources for a case."""
        for source in sources:
            self.grant(subject, source, "read")
