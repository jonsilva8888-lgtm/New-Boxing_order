"""Weighted round-by-round fight simulation for Iron Road Boxing Manager."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
import random
from .fighter import Fighter
from .utils import clamp, weighted_choice

STYLE_MODIFIERS: dict[str, dict[str, float]] = {
    "Pressure Fighter": {"pace": 8, "defense": -2, "body": 3, "late": 1},
    "Out Boxer": {"pace": -5, "defense": 6, "range": 5, "late": 0},
    "Counter Puncher": {"pace": -6, "defense": 3, "counter": 7, "late": 0},
    "Technician": {"pace": -1, "defense": 4, "iq": 5, "late": 1},
    "Slugger": {"pace": 3, "defense": -5, "power": 8, "late": -1},
    "Volume Puncher": {"pace": 10, "defense": -1, "late": 2},
    "Swarmer": {"pace": 12, "defense": -3, "body": 4, "late": -1},
    "Switch Hitter": {"pace": 1, "defense": 2, "iq": 3, "counter": 3, "late": 0},
}

@dataclass(slots=True)
class RoundReport:
    """Detailed data for one simulated round."""
    number: int
    winner: str
    red_score: int
    blue_score: int
    red_landed: int
    blue_landed: int
    knockdowns: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

@dataclass(slots=True)
class FightResult:
    """Serializable output from a fight simulation."""
    winner: str | None
    loser: str | None
    method: str
    rounds: int
    summary: list[str]
    scorecards: list[tuple[int, int]]
    stats: dict[str, dict[str, int]]
    fight_rating: int
    round_reports: list[RoundReport] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

class FightEngine:
    """Simulates boxing without player punch control.

    The model is deterministic in structure but not outcome: fighter attributes build a
    weighted expectation for pace, accuracy, defense, hurt potential, late-fight fade,
    and judging. Random variance is intentionally smaller than ratings impact so elite
    fighters usually look elite while upsets still happen.
    """

    def simulate(self, red: Fighter, blue: Fighter, scheduled_rounds: int = 12, title: bool = False) -> FightResult:
        points = {red.name: 0, blue.name: 0}
        damage = {red.name: 0, blue.name: 0}
        momentum = {red.name: 0.0, blue.name: 0.0}
        stats = {red.name: {"thrown": 0, "landed": 0, "knockdowns": 0, "cuts": 0}, blue.name: {"thrown": 0, "landed": 0, "knockdowns": 0, "cuts": 0}}
        reports: list[RoundReport] = []
        summary: list[str] = [f"Opening bell: {red.name} faces {blue.name}{' for a title' if title else ''}."]

        for rnd in range(1, scheduled_rounds + 1):
            red_line = self._round_output(red, blue, rnd, scheduled_rounds, momentum[red.name], damage[red.name])
            blue_line = self._round_output(blue, red, rnd, scheduled_rounds, momentum[blue.name], damage[blue.name])
            for fighter, line in ((red, red_line), (blue, blue_line)):
                stats[fighter.name]["thrown"] += line["thrown"]
                stats[fighter.name]["landed"] += line["landed"]

            red_value = red_line["value"] - blue.effective("defense") * 0.08
            blue_value = blue_line["value"] - red.effective("defense") * 0.08
            round_winner = red if red_value >= blue_value else blue
            round_loser = blue if round_winner is red else red
            knockdowns: list[str] = []
            notes: list[str] = []

            for attacker, defender, line in ((red, blue, red_line), (blue, red, blue_line)):
                hurt = self._hurt_score(attacker, defender, line["landed"], damage[defender.name])
                damage[defender.name] += max(0, int(line["landed"] / 5 + hurt / 9))
                if hurt > 32 and random.random() < min(0.55, hurt / 125):
                    stats[attacker.name]["knockdowns"] += 1
                    knockdowns.append(defender.name)
                    notes.append(f"{attacker.name} floors {defender.name}.")
                    if hurt > 55 and random.random() > defender.effective("heart") / 118:
                        return self._stoppage(attacker, defender, rnd, points, stats, damage, reports, summary, "KO")
                if hurt > 24 and random.random() < defender.hidden["cut_susceptibility"] / 450:
                    stats[attacker.name]["cuts"] += 1
                    notes.append(f"A cut opens near {defender.name}'s eye.")
                if damage[defender.name] > 70 and random.random() < (damage[defender.name] - 60) / 150:
                    return self._stoppage(attacker, defender, rnd, points, stats, damage, reports, summary, weighted_choice([("TKO", 5), ("Doctor Stoppage", 2), ("Corner Retirement", 1)]))

            red_score, blue_score = self._score_round(red, blue, round_winner, knockdowns)
            points[red.name] += red_score
            points[blue.name] += blue_score
            momentum[round_winner.name] += 0.9
            momentum[round_loser.name] -= 0.5
            reports.append(RoundReport(rnd, round_winner.name, red_score, blue_score, red_line["landed"], blue_line["landed"], knockdowns, notes))
            if notes or abs(red_value - blue_value) < 4:
                summary.append(f"Round {rnd}: " + (" ".join(notes) if notes else "a tactical swing round divides observers."))

        return self._decision(red, blue, points, stats, damage, reports, summary)

    def _round_output(self, fighter: Fighter, opponent: Fighter, rnd: int, scheduled: int, momentum: float, absorbed: int) -> dict[str, int | float]:
        mod = STYLE_MODIFIERS.get(fighter.style, {})
        fatigue_drag = fighter.fatigue * 0.22 + absorbed * 0.10 + max(0, rnd - scheduled * 0.6) * (2 - mod.get("late", 0))
        range_edge = (fighter.reach - opponent.reach) * 0.55 + (fighter.height - opponent.height) * 0.20 + mod.get("range", 0)
        pace = 39 + mod.get("pace", 0) + fighter.effective("stamina") * 0.20 + fighter.effective("aggression") * 0.13 - fatigue_drag * 0.20
        thrown = clamp(random.gauss(pace, 6), 12, 92)
        accuracy = 22 + fighter.effective("accuracy") * 0.22 + fighter.effective("ring_iq") * 0.10 + range_edge * 0.35 + momentum * 0.3
        defensive_shadow = opponent.effective("defense") * 0.15 + opponent.effective("head_movement") * 0.12 + opponent.effective("footwork") * 0.08
        land_rate = clamp(random.gauss(accuracy - defensive_shadow, 4), 8, 62)
        landed = int(thrown * land_rate / 100)
        value = landed + fighter.effective("power") * 0.08 + fighter.effective("body_punching") * 0.04 + mod.get("iq", 0) + mod.get("counter", 0)
        return {"thrown": int(thrown), "landed": landed, "value": value}

    def _hurt_score(self, attacker: Fighter, defender: Fighter, landed: int, defender_damage: int) -> float:
        return max(0, attacker.effective("power") * 0.72 + landed * 0.75 - defender.effective("chin") * 0.55 - defender.hidden["punch_resistance"] * 0.20 + defender_damage * 0.12 + random.gauss(0, 10))

    def _score_round(self, red: Fighter, blue: Fighter, winner: Fighter, knockdowns: list[str]) -> tuple[int, int]:
        red_score = blue_score = 9
        if winner is red: red_score = 10
        else: blue_score = 10
        red_score -= knockdowns.count(red.name)
        blue_score -= knockdowns.count(blue.name)
        return max(6, red_score), max(6, blue_score)

    def _stoppage(self, winner: Fighter, loser: Fighter, rnd: int, points: dict[str, int], stats: dict[str, dict[str, int]], damage: dict[str, int], reports: list[RoundReport], summary: list[str], method: str) -> FightResult:
        self._apply_result(winner, loser, method, damage)
        summary.append(f"{winner.name} defeats {loser.name} by {method} in round {rnd}.")
        return FightResult(winner.name, loser.name, method, rnd, summary, [], stats, self._rating(damage, stats), reports)

    def _decision(self, red: Fighter, blue: Fighter, points: dict[str, int], stats: dict[str, dict[str, int]], damage: dict[str, int], reports: list[RoundReport], summary: list[str]) -> FightResult:
        red_total, blue_total = points[red.name], points[blue.name]
        cards = [(red_total + random.randint(-2, 2), blue_total + random.randint(-2, 2)) for _ in range(3)]
        red_cards = sum(r > b for r, b in cards)
        blue_cards = sum(b > r for r, b in cards)
        if red_cards == blue_cards:
            red.record.draws += 1; blue.record.draws += 1
            summary.append("The judges cannot separate them: draw.")
            return FightResult(None, None, "Draw", len(reports), summary, cards, stats, self._rating(damage, stats), reports)
        winner, loser = (red, blue) if red_cards > blue_cards else (blue, red)
        method = "Unanimous Decision" if max(red_cards, blue_cards) == 3 else "Split Decision"
        if any(r == b for r, b in cards): method = "Majority Decision"
        self._apply_result(winner, loser, method, damage)
        summary.append(f"After {len(reports)} rounds, {winner.name} wins by {method}.")
        return FightResult(winner.name, loser.name, method, len(reports), summary, cards, stats, self._rating(damage, stats), reports)

    def _apply_result(self, winner: Fighter, loser: Fighter, method: str, damage: dict[str, int]) -> None:
        winner.record.wins += 1
        loser.record.losses += 1
        if method in {"KO", "TKO", "Corner Retirement", "Doctor Stoppage"}:
            winner.record.ko_wins += 1
            loser.record.ko_losses += 1
            loser.stats["chin"] = clamp(loser.stats["chin"] - 2)
            loser.stats["recovery"] = clamp(loser.stats["recovery"] - 2)
            loser.hidden["durability"] = clamp(loser.hidden["durability"] - 1)
        winner.popularity += 2 + (2 if loser.ranking <= 15 else 0)
        loser.popularity -= 1
        winner.quality_wins += 1 if loser.ranking <= 15 else 0
        for fighter in (winner, loser):
            fighter.career_damage += int(damage[fighter.name] / 15)
            fighter.fatigue = clamp(fighter.fatigue + 10, 0, 100)

    def _rating(self, damage: dict[str, int], stats: dict[str, dict[str, int]]) -> int:
        action = sum(v["landed"] for v in stats.values()) / 3
        drama = sum(v["knockdowns"] for v in stats.values()) * 14 + sum(v["cuts"] for v in stats.values()) * 5
        punishment = sum(damage.values()) * 0.55
        return clamp(action + drama + punishment, 1, 100)
