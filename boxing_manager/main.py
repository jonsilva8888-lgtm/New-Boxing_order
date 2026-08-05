"""Terminal UI for Iron Road Boxing Manager."""
from __future__ import annotations

from .career import Career
from .constants import TRAINING_TYPES
from .save_manager import list_saves, save_game
from .utils import money


def choose(items: list[object], title: str) -> int:
    print(f"\n{title}")
    for index, item in enumerate(items, 1):
        print(f"{index}. {item}")
    try:
        return int(input("> ")) - 1
    except (ValueError, EOFError):
        return -1


def show(career: Career) -> None:
    player = career.player
    print(f"\n{carrer_label(career)}")
    print(f"{player.name} '{player.nickname}' | {player.record.text()} | Rank #{player.ranking} | OVR {player.overall} | Cash {money(player.cash)}")
    print(f"Age {player.age} | Pop {player.popularity} | Weight {player.weight:.1f}/160 | Fatigue {player.fatigue} | Belts {', '.join(player.current_belts) or 'None'}")
    print(f"Coach {career.coach.name} ({career.coach.tier}) | Sponsor {career.sponsor.name if career.sponsor else 'None'} | HOF {career.hof_score()}")
    if player.injuries:
        print("Injuries:", ", ".join(f"{name} ({weeks}w)" for name, weeks in player.injuries.items()))
    if career.camp:
        print(f"Camp: {career.camp.weeks_left}/{career.camp.weeks_total} weeks left")


def carrer_label(career: Career) -> str:
    return f"{career.calendar.label()} | Iron Road Boxing Manager"


def new_or_load() -> Career:
    saves = list_saves()
    options = ["New Career"] + [f"Load {slot}" for slot in saves]
    pick = choose(options, "Main Menu")
    if pick > 0 and pick - 1 < len(saves):
        return Career.from_slot(saves[pick - 1])
    name = input("Fighter name [Player Prospect]: ").strip() or "Player Prospect"
    career = Career()
    career.player.name = name
    return career


def main() -> None:
    print("IRON ROAD BOXING MANAGER")
    career = new_or_load()
    while True:
        show(career)
        menu = ["Train", "Start Camp", "Rankings", "Belts", "Schedule Fight", "Finance", "World News", "Social Feed", "Career Stats", "Rivalries", "Save", "Exit"]
        pick = choose(menu, "Career Hub")
        if pick == 0:
            ix = choose(TRAINING_TYPES, "Training Plan")
            print(career.train_week(TRAINING_TYPES[ix] if ix in range(len(TRAINING_TYPES)) else "Rest"))
        elif pick == 1:
            lengths = [4, 6, 8, 10, 12]
            ix = choose(lengths, "Camp Length")
            print(career.start_camp(lengths[ix] if ix in range(len(lengths)) else 4))
        elif pick == 2:
            for fighter in career.division.fighters[:50]:
                belts = ",".join(fighter.current_belts) or "-"
                print(f"#{fighter.ranking:02d} {fighter.name:22} {fighter.record.text():14} OVR {fighter.overall:02d} Age {fighter.age} Belts {belts}")
        elif pick == 3:
            for belt, holder in career.division.belts.holders.items():
                print(f"{belt}: {holder or 'Vacant'}")
        elif pick == 4:
            opponents = career.division.opponents_for(career.player)
            ix = choose([f"#{opponent.ranking} {opponent.name} {opponent.record.text()} OVR {opponent.overall} {'TITLE' if opponent.current_belts else ''}" for opponent in opponents], "Available Opponents")
            if ix in range(len(opponents)):
                try:
                    result, purse = career.fight(opponents[ix])
                    print("\n".join(result.summary))
                    print("Scorecards:", result.scorecards or "stoppage")
                    print("Purse:", money(purse))
                except ValueError as exc:
                    print(f"Fight not made: {exc}")
        elif pick == 5:
            sponsor = career.sign_best_sponsor()
            print(f"Coach {career.coach.name}; Sponsor {sponsor.name if sponsor else 'none available'}; Cash {money(career.player.cash)}")
        elif pick == 6:
            print("\n".join(career.news.articles[:12]) or "No news yet.")
        elif pick == 7:
            print("\n".join(career.social.posts[:12]) or "No posts yet.")
        elif pick == 8:
            print(career.player)
        elif pick == 9:
            print(career.rivalries or "No rivalries yet.")
        elif pick == 10:
            slot = input("Save slot [manual]: ").strip() or "manual"
            print("Saved", save_game(career, slot))
        elif pick == 11:
            break


if __name__ == "__main__":
    main()
