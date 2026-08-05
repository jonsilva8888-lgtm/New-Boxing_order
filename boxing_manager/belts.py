"""Belt registry."""
from dataclasses import dataclass, field
from .constants import BELT_NAMES
@dataclass
class BeltRegistry:
    holders: dict[str,str|None]=field(default_factory=lambda:{b:None for b in BELT_NAMES})
    def award(self,belt:str,winner,loser=None):
        self.holders[belt]=winner.name
        if belt not in winner.current_belts: winner.current_belts.append(belt)
        if loser and belt in loser.current_belts: loser.current_belts.remove(belt)
