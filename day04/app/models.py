"""Dataclass for a PoshanGuide record."""
from dataclasses import dataclass, asdict


@dataclass
class Record:
    guideline_no: int
    guideline_title: str
    key_advice: str
    number_limit: str = ""
    target_group: str = "All Indians"
    page_ref: str = "TBD"
    id: int = 0

    def to_dict(self):
        return asdict(self)
