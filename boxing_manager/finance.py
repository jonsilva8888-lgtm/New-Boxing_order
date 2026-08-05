"""Finance helpers."""
from .constants import WEEKLY_LIVING_COST, WEEKLY_CAMP_COST
def purse_for_rank(rank:int, title:bool=False)->tuple[int,int]:
    if title: return (500_000,5_000_000)
    if rank<=5: return (250_000,750_000)
    if rank<=15: return (75_000,250_000)
    if rank<=30: return (20_000,75_000)
    return (4_000,20_000)
def charge_week(fighter,in_camp:bool, coach_cost:int=0, sponsor_income:int=0)->int:
    delta=sponsor_income-WEEKLY_LIVING_COST-(WEEKLY_CAMP_COST if in_camp else 0)-coach_cost
    fighter.cash+=delta; return delta
