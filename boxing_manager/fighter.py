"""Fighter model and career progression."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
import random
from .constants import CORE_STATS, HIDDEN_STATS, STANCES, STYLES, NATIONALITIES, WEIGHT_LIMIT
from .utils import clamp

FIRST = "Aaron Andre Arturo Ben Caleb Dante Diego Ellis Enzo Felix Gabriel Hector Ivan Jamal Karim Leo Mateo Nico Oscar Pavel Rafael Silas Tomas Victor Wesley Yuri Zion".split()
LAST = "Stone Cruz Bennett Alvarez Ward Price Okoro Hayes Mori Silva Brooks Kelly Torres Reed Novak Santos King Walsh Ortiz Khan Brooks".split()
NICKS = ["Iron", "Road", "Flash", "Hammer", "Saint", "Wolf", "Storm", "Professor", "Cyclone", "Ghost", "Bull", "Ace"]

@dataclass
class Record:
    wins: int = 0; losses: int = 0; draws: int = 0
    ko_wins: int = 0; ko_losses: int = 0
    def text(self) -> str: return f"{self.wins}-{self.losses}-{self.draws} ({self.ko_wins} KO)"

@dataclass
class Fighter:
    name: str
    nickname: str
    nationality: str
    age: int
    height: int
    reach: int
    stance: str
    style: str
    stats: dict[str, int]
    hidden: dict[str, int]
    record: Record = field(default_factory=Record)
    ranking: int = 50
    current_belts: list[str] = field(default_factory=list)
    injuries: dict[str, int] = field(default_factory=dict)
    prime_start: int = 25
    prime_end: int = 32
    career_damage: int = 0
    money_earned: int = 0
    cash: int = 0
    manager: str = "Independent"
    promoter: str | None = None
    fatigue: int = 0
    weight: float = 160.0
    retired: bool = False
    is_player: bool = False
    title_defenses: int = 0
    quality_wins: int = 0
    fight_of_year: int = 0

    @property
    def overall(self) -> int:
        keys = [k for k in CORE_STATS if k not in {"popularity", "marketability"}]
        return clamp(sum(self.stats[k] for k in keys) / len(keys))

    @property
    def popularity(self) -> int: return self.stats["popularity"]
    @popularity.setter
    def popularity(self, v: int) -> None: self.stats["popularity"] = clamp(v, 0, 100)

    def effective(self, stat: str) -> int:
        penalty = self.fatigue * 0.18 + self.career_damage * 0.08 + max(0, self.weight - WEIGHT_LIMIT) * 2
        if self.injuries: penalty += 6
        return clamp(self.stats[stat] - penalty, 1, 100)

    def train_stat(self, stat: str, amount: float) -> None:
        cap = max(self.overall, self.hidden["potential"])
        self.stats[stat] = clamp(self.stats[stat] + amount * self.hidden["learning_speed"] / 60, 1, cap)

    def age_one_year(self) -> None:
        self.age += 1
        if self.age > self.prime_end:
            decline = max(1, self.hidden["decline_speed"] / 28)
            for k in self.stats:
                if k not in {"popularity", "marketability"}: self.stats[k] = clamp(self.stats[k] - decline)

    def tick_injuries(self) -> None:
        self.injuries = {k: v - 1 for k, v in self.injuries.items() if v > 1}

    def to_dict(self) -> dict:
        d = asdict(self); d["record"] = asdict(self.record); return d

    @classmethod
    def from_dict(cls, data: dict) -> "Fighter":
        data = dict(data); data["record"] = Record(**data["record"]); return cls(**data)


def create_player(name: str = "Player Prospect") -> Fighter:
    stats = {k: 60 for k in CORE_STATS}; stats["popularity"] = 0; stats["marketability"] = 35
    hidden = {k: 60 for k in HIDDEN_STATS}; hidden.update({"potential": 86, "learning_speed": 72, "prime_length": 9, "mental_toughness": 72})
    return Fighter(name, "Unknown", "USA", 18, 71, 73, "Orthodox", "Technician", stats, hidden, cash=2500, ranking=50, weight=162.0, is_player=True)

def random_fighter(ranking: int) -> Fighter:
    age = random.randint(19, 37); potential = random.randint(58, 96); base = clamp(random.gauss(78 - ranking * .35, 8), 45, 94)
    stats = {k: clamp(random.gauss(base, 10)) for k in CORE_STATS}; stats["popularity"] = clamp(70 - ranking + random.randint(-10, 18), 0, 100); stats["marketability"] = clamp(stats["popularity"] + random.randint(-15, 15), 0, 100)
    hidden = {k: random.randint(35, 90) for k in HIDDEN_STATS}; hidden["potential"] = potential
    wins = max(0, random.randint(0, 32) - ranking // 5); losses = random.randint(0, min(8, ranking // 6)); kos = random.randint(0, wins)
    return Fighter(f"{random.choice(FIRST)} {random.choice(LAST)}", random.choice(NICKS), random.choice(NATIONALITIES), age, random.randint(68, 75), random.randint(68, 78), random.choice(STANCES), random.choice(STYLES), stats, hidden, Record(wins, losses, random.randint(0,2), kos, random.randint(0, losses)), ranking=ranking, weight=random.uniform(158, 166))
