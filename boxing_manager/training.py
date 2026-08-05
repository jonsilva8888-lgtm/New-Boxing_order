"""Training system."""
from __future__ import annotations
from .fighter import Fighter
from .utils import clamp
EFFECTS = {"Strength":{"power":2,"conditioning":1},"Speed":{"speed":2,"footwork":1},"Roadwork":{"stamina":2,"conditioning":2},"Sparring":{"ring_iq":1,"defense":1,"heart":1,"accuracy":1},"Technical":{"defense":1,"footwork":1,"accuracy":1,"head_movement":1},"Heavy Bag":{"power":1,"body_punching":2,"aggression":1},"Mitt Work":{"accuracy":2,"counter_punching":1,"speed":1},"Film Study":{"ring_iq":2,"discipline":1,"counter_punching":1},"Recovery":{},"Rest":{}}
def train(fighter: Fighter, kind: str, in_camp: bool, coach_multiplier: float = 1.0) -> str:
    if kind in {"Recovery","Rest"}:
        fighter.fatigue = clamp(fighter.fatigue - (14 if kind == "Rest" else 10), 0, 100); fighter.weight += .4 if kind == "Rest" else .1; return f"{fighter.name} recovers; fatigue is {fighter.fatigue}."
    mult = (1.0 if in_camp else .25) * coach_multiplier
    for stat, amt in EFFECTS[kind].items(): fighter.train_stat(stat, amt * mult)
    fighter.fatigue = clamp(fighter.fatigue + (9 if in_camp else 4), 0, 100)
    fighter.weight += -1.0 if kind == "Roadwork" else .2
    return f"{fighter.name} completed {kind}. Overall {fighter.overall}, fatigue {fighter.fatigue}, weight {fighter.weight:.1f}."
