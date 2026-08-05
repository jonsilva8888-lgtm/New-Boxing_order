"""Weekly calendar."""
from dataclasses import dataclass
@dataclass
class GameCalendar:
    year:int=2026; week:int=1
    def advance(self):
        self.week+=1
        if self.week>52: self.week=1; self.year+=1
    def label(self)->str: return f"Year {self.year}, Week {self.week}"
