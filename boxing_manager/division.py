"""Living middleweight division that keeps operating without the player."""
from __future__ import annotations

import random
from .fighter import Fighter, random_fighter
from .rankings import update_rankings
from .fight_engine import FightEngine
from .belts import BeltRegistry
from .news import NewsDesk
from .social_media import SocialFeed
from .training import train
from .injuries import maybe_injure
from .constants import MAX_ACTIVE_FIGHTERS, BELT_NAMES

class Division:
    """Owns fighters, belts, rankings, AI fights, retirement, and prospect intake."""

    def __init__(self, fighters: list[Fighter] | None = None, belts: BeltRegistry | None = None):
        self.fighters = fighters or [random_fighter(i) for i in range(1, MAX_ACTIVE_FIGHTERS + 1)]
        self.belts = belts or BeltRegistry()
        self.engine = FightEngine()
        update_rankings(self.fighters)
        if not any(self.belts.holders.values()):
            champion = min(self.fighters, key=lambda fighter: fighter.ranking)
            for belt in BELT_NAMES:
                self.belts.award(belt, champion)

    def add_player(self, player: Fighter) -> None:
        if player not in self.fighters:
            self.fighters.append(player)
        update_rankings(self.fighters)

    def weekly_ai(self, news: NewsDesk, social: SocialFeed) -> None:
        """Advance every non-player boxer by a week and schedule independent AI bouts."""
        active = [fighter for fighter in self.fighters if not fighter.retired and not fighter.is_player]
        for fighter in active:
            fighter.tick_injuries()
            if not fighter.injuries:
                train(fighter, random.choice(["Roadwork", "Technical", "Sparring", "Film Study", "Recovery"]), fighter.ranking <= 20, 1.0)
                injury = maybe_injure(fighter, 8)
                if injury:
                    news.add(f"Training setback: {fighter.name} suffers {injury} and will miss time.")
            fighter.weight += random.uniform(-0.7, 0.8)

        self._make_ai_fights(active, news, social)
        self._retire_and_replace(news)
        self._defend_vacant_belts(news)
        update_rankings(self.fighters)

    def opponents_for(self, player: Fighter) -> list[Fighter]:
        ranked = update_rankings(self.fighters)
        available = [fighter for fighter in ranked if fighter is not player and not fighter.retired and not fighter.injuries]
        if player.ranking > 35:
            return available[28:50]
        if player.ranking > 15:
            return available[12:36]
        return available[:20]

    def _make_ai_fights(self, active: list[Fighter], news: NewsDesk, social: SocialFeed) -> None:
        pools = [sorted(active, key=lambda fighter: fighter.ranking)[:16], sorted(active, key=lambda fighter: fighter.ranking)[16:36], sorted(active, key=lambda fighter: fighter.ranking)[36:]]
        for pool in pools:
            random.shuffle(pool)
            for red, blue in zip(pool[::2], pool[1::2]):
                if red.injuries or blue.injuries or random.random() > 0.09:
                    continue
                title_belts = list(red.current_belts or blue.current_belts)
                result = self.engine.simulate(red, blue, 12 if title_belts else 10, bool(title_belts))
                if result.winner:
                    winner = red if result.winner == red.name else blue
                    loser = blue if winner is red else red
                    for belt in title_belts:
                        self.belts.award(belt, winner, loser)
                social.react(result)
                if result.fight_rating >= 80:
                    for fighter in (red, blue):
                        fighter.fight_of_year += 1
                    news.add(f"Fight of the year contender: {red.name} and {blue.name} deliver a {result.fight_rating}/100 classic.")
                elif result.winner and abs(red.ranking - blue.ranking) >= 14:
                    news.add(f"Upset alert: {result.winner} rewrites the middleweight rankings.")

    def _retire_and_replace(self, news: NewsDesk) -> None:
        for fighter in self.fighters:
            if fighter.retired or fighter.is_player:
                continue
            age_pressure = max(0, fighter.age - 36) * 4
            damage_pressure = fighter.career_damage
            losing_pressure = max(0, fighter.record.losses - fighter.record.wins) * 5
            if random.random() < (age_pressure + damage_pressure + losing_pressure) / 1800:
                fighter.retired = True
                for belt in list(fighter.current_belts):
                    fighter.current_belts.remove(belt)
                    self.belts.holders[belt] = None
                news.add(f"{fighter.name} retires with a record of {fighter.record.text()}.")
        while len([fighter for fighter in self.fighters if not fighter.retired]) < MAX_ACTIVE_FIGHTERS + 1:
            prospect = random_fighter(MAX_ACTIVE_FIGHTERS)
            self.fighters.append(prospect)
            news.add(f"New prospect {prospect.name} turns professional at middleweight.")

    def _defend_vacant_belts(self, news: NewsDesk) -> None:
        ranked = update_rankings([fighter for fighter in self.fighters if not fighter.retired])
        for belt, holder in list(self.belts.holders.items()):
            if holder is None and ranked:
                self.belts.award(belt, ranked[0])
                news.add(f"{ranked[0].name} is recognized as the new {belt} champion after the belt becomes vacant.")
