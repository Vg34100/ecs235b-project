from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class AccessControlMatrix:
    """Simple ACM for tracking read/write/influence rights.

    The ACM is intentionally small for now. The main point is just to keep the
    source/subject relationships explicit in code.
    """

    matrix: Dict[str, Dict[str, Set[str]]] = field(default_factory=dict)

    def grant(self, subject: str, obj: str, right: str) -> None:
        # Nested dict-of-sets is enough here and stays easy to read.
        self.matrix.setdefault(subject, {}).setdefault(obj, set()).add(right)

    def has_right(self, subject: str, obj: str, right: str) -> bool:
        return right in self.matrix.get(subject, {}).get(obj, set())

    def from_case_defaults(self, subject: str, sources: list[str]) -> None:
        # Quick helper for building a case-level ACM from a source list.
        for source in sources:
            self.grant(subject, source, "read")
