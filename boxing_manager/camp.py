"""Training camp state."""
from dataclasses import dataclass
@dataclass
class Camp:
    weeks_total:int; weeks_left:int
    @classmethod
    def start(cls,weeks:int):
        if weeks not in {4,6,8,10,12}: raise ValueError("Camp must be 4, 6, 8, 10, or 12 weeks")
        return cls(weeks,weeks)
