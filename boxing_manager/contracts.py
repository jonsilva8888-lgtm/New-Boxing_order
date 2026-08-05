"""Fight offer and negotiation."""
from dataclasses import dataclass
@dataclass
class FightOffer:
    opponent_name:str; purse:int; weeks:int; title:bool=False
    def counter_more_money(self): self.purse=int(self.purse*1.15); return self
    def request_more_camp(self): self.weeks+=2; return self
