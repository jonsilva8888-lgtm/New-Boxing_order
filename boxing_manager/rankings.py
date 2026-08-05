"""Ranking calculations."""
def update_rankings(fighters):
    active=[f for f in fighters if not f.retired]
    active.sort(key=lambda f:(len(f.current_belts), f.record.wins*3-f.record.losses*4+f.overall+f.popularity/3), reverse=True)
    for i,f in enumerate(active,1): f.ranking=i
    return active
