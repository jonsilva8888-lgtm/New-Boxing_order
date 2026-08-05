"""Career orchestration for the player and the autonomous boxing world."""
from __future__ import annotations

import random
from .fighter import Fighter, create_player
from .division import Division
from .calendar import GameCalendar
from .news import NewsDesk
from .social_media import SocialFeed
from .camp import Camp
from .coach import COACHES, Coach
from .sponsors import SPONSORS, Sponsor
from .finance import charge_week, purse_for_rank
from .training import train
from .fight_engine import FightEngine, FightResult
from .save_manager import save_game, load_raw
from .rankings import update_rankings
from .hall_of_fame import score
from .belts import BeltRegistry
from .injuries import maybe_injure

class Career:
    """Facade used by the UI and tests to play a full boxing career."""

    def __init__(self, player: Fighter | None = None, division: Division | None = None):
        self.player = player or create_player()
        self.calendar = GameCalendar()
        self.division = division or Division()
        self.division.add_player(self.player)
        self.news = NewsDesk()
        self.social = SocialFeed()
        self.camp: Camp | None = None
        self.coach: Coach = COACHES[0]
        self.sponsor: Sponsor | None = None
        self.engine = FightEngine()
        self.rivalries: dict[str, int] = {}

    def start_camp(self, weeks: int) -> str:
        self.camp = Camp.start(weeks)
        message = f"{self.player.name} opens a {weeks}-week camp. Training gains and costs increase."
        self.news.add(message)
        return message

    def train_week(self, kind: str) -> str:
        message = train(self.player, kind, self.camp is not None, self.coach.multiplier)
        injury = maybe_injure(self.player, 14 if self.camp else 6)
        if injury:
            message += f" Injury scare: {injury}."
            self.news.add(f"Camp report: {self.player.name} is dealing with {injury}.")
        self.advance_week()
        return message

    def advance_week(self) -> None:
        if self.camp:
            self.camp.weeks_left -= 1
            if self.camp.weeks_left <= 0:
                self.camp = None
                self.news.add("Camp wraps up. The work is banked; now the lights await.")
        self.player.tick_injuries()
        self.player.weight += random.uniform(-0.4, 0.9)
        delta = charge_week(self.player, self.camp is not None, self.coach.weekly_cost, self.sponsor.weekly_pay if self.sponsor else 0)
        if delta < 0 and self.player.cash < 0:
            self.news.add(f"Financial pressure mounts as {self.player.name}'s balance drops below zero.")
        self.division.weekly_ai(self.news, self.social)
        self.calendar.advance()
        if self.calendar.week == 1:
            for fighter in self.division.fighters:
                fighter.age_one_year()
        save_game(self, "autosave")

    def fight(self, opponent: Fighter) -> tuple[FightResult, int]:
        if opponent.retired or opponent.injuries:
            raise ValueError("Opponent is not available")
        if self.player.injuries:
            raise ValueError("You cannot fight while injured")
        title = bool(opponent.current_belts)
        if self.player.weight > 162.0:
            self.player.cash -= 2_500
            self.player.popularity -= 2
            if random.random() < 0.25:
                self.news.add(f"{self.player.name} misses weight and the bout is cancelled.")
                self.advance_week()
                raise ValueError("Fight cancelled after missing weight")
        result = self.engine.simulate(self.player, opponent, 12 if title else 10, title)
        purse = random.randint(*purse_for_rank(opponent.ranking, title))
        self.player.cash += purse
        self.player.money_earned += purse
        if result.winner == self.player.name:
            for belt in list(opponent.current_belts):
                self.division.belts.award(belt, self.player, opponent)
        if result.method in {"Split Decision", "Draw"} or result.fight_rating > 78:
            self.rivalries[opponent.name] = self.rivalries.get(opponent.name, 0) + 1
        self.social.react(result)
        self.news.add(result.summary[-1])
        update_rankings(self.division.fighters)
        self.advance_week()
        return result, purse

    def sign_best_sponsor(self) -> Sponsor | None:
        eligible = [sponsor for sponsor in SPONSORS if self.player.popularity >= sponsor.min_popularity]
        self.sponsor = eligible[-1] if eligible else None
        if self.sponsor:
            self.news.add(f"{self.player.name} signs a {self.sponsor.category} deal with {self.sponsor.name}.")
        return self.sponsor

    def hof_score(self) -> int:
        return score(self.player)

    def to_dict(self) -> dict:
        return {
            "player": self.player.to_dict(),
            "calendar": self.calendar.__dict__,
            "fighters": [fighter.to_dict() for fighter in self.division.fighters],
            "belts": self.division.belts.holders,
            "news": self.news.articles,
            "social": self.social.posts,
            "camp": self.camp.__dict__ if self.camp else None,
            "coach": self.coach.name,
            "sponsor": self.sponsor.name if self.sponsor else None,
            "rivalries": self.rivalries,
        }

    @classmethod
    def from_slot(cls, slot: str) -> "Career":
        data = load_raw(slot)
        fighters = [Fighter.from_dict(item) for item in data["fighters"]]
        player = next((fighter for fighter in fighters if fighter.is_player), Fighter.from_dict(data["player"]))
        belts = BeltRegistry(data.get("belts", {}))
        career = cls(player, Division(fighters, belts))
        career.calendar = GameCalendar(**data.get("calendar", {}))
        career.news.articles = data.get("news", [])[:50]
        career.social.posts = data.get("social", [])[:50]
        if data.get("camp"):
            career.camp = Camp(**data["camp"])
        career.coach = next((coach for coach in COACHES if coach.name == data.get("coach")), COACHES[0])
        career.sponsor = next((sponsor for sponsor in SPONSORS if sponsor.name == data.get("sponsor")), None)
        career.rivalries = data.get("rivalries", {})
        return career
