"""Coach catalogue."""
from dataclasses import dataclass
@dataclass
class Coach:
    name: str; tier: str; weekly_cost: int; multiplier: float
COACHES=[Coach("Mickey Doyle","Local",100,1.0),Coach("Rosa Vega","Regional",500,1.18),Coach("Ibrahim Price","Elite",1800,1.38),Coach("Naomi Legend","Legendary",6000,1.65)]
