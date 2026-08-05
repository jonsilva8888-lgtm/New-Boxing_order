"""Injury generation."""
import random
INJURIES={"Broken Hand":8,"Rib Injury":6,"Shoulder":7,"Concussion":10,"Cut":3,"Broken Nose":5,"Sprained Ankle":4}
def maybe_injure(fighter, intensity:int=10):
    risk=(fighter.hidden["injury_risk"]*0.35+fighter.fatigue*0.45+intensity)/1200
    if random.random()<risk:
        name=random.choice(list(INJURIES)); fighter.injuries[name]=INJURIES[name]; return name
    return None
