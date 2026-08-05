"""Hall of fame scoring."""
def score(f):
    return f.record.wins*4 - f.record.losses*3 + len(f.current_belts)*35 + f.title_defenses*8 + f.quality_wins*6 + f.popularity + f.fight_of_year*12
