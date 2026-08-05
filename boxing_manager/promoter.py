"""Promoters and relationships."""
from dataclasses import dataclass
@dataclass
class Promoter:
    name: str; reach: int; purse_bonus: float; relationship: int = 50
PROMOTERS=[Promoter("Brickhouse Boxing",35,.05),Promoter("Atlantic Fight Club",55,.15),Promoter("Global Crown Promotions",78,.30),Promoter("Titan Ring Sports",92,.45)]
