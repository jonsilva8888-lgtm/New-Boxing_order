"""Event scheduling primitives."""
from __future__ import annotations
from dataclasses import dataclass, field
from .fighter import Fighter

@dataclass
class Event:
    """A boxing event containing one or more simulated bouts."""
    name: str
    week_label: str
    bouts: list[tuple[Fighter, Fighter, bool]] = field(default_factory=list)
    completed: bool = False

    def add_bout(self, red: Fighter, blue: Fighter, title: bool = False) -> None:
        self.bouts.append((red, blue, title))

    def headline(self) -> str:
        if not self.bouts:
            return f"{self.name}: card to be announced"
        red, blue, title = self.bouts[0]
        suffix = " for championship gold" if title else ""
        return f"{self.name}: {red.name} vs {blue.name}{suffix}"
