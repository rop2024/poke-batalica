from battle import Battle, BattleParticipant, BattlePokemon
from pokemon import fetch_pokemon


def choose_pokemon(prompt: str) -> BattlePokemon:
    while True:
        name = input(f"{prompt} (enter a Pokemon name): ").strip()
        if not name:
            print("Please enter a name.")
            continue
        try:
            species = fetch_pokemon(name)
        except ValueError as exc:
            print(exc)
            continue
        max_hp = species.base_hp
        return BattlePokemon(species=species, current_hp=max_hp, max_hp=max_hp)


def pick_move(participant: BattleParticipant) -> str:
    pokemon = participant.pokemon.species
    print(f"\n{participant.name}'s {pokemon.name} (HP {participant.pokemon.current_hp}/{participant.pokemon.max_hp})")
    for idx, move in enumerate(pokemon.moves, start=1):
        print(f"  {idx}. {move.name} (power={move.power}, type={move.move_type})")
    while True:
        choice = input(f"Choose a move for {pokemon.name} (1-{len(pokemon.moves)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(pokemon.moves):
            return pokemon.moves[int(choice) - 1].name
        print("Invalid choice, try again.")


def hp_bar(participant: BattleParticipant, width: int = 20) -> str:
    p = participant.pokemon
    filled = int(width * p.hp_percent)
    return f"[{'#' * filled}{'-' * (width - filled)}] {p.current_hp}/{p.max_hp}"


def show_state(battle: Battle) -> None:
    print("\n--- Battle State ---")
    print(f"{battle.player_a.name}: {hp_bar(battle.player_a)}  {battle.player_a.pokemon.species.name}")
    print(f"{battle.player_b.name}: {hp_bar(battle.player_b)}  {battle.player_b.pokemon.species.name}")
    print("--------------------\n")


def main() -> None:
    print("=== Pokemon Battle MVP (local, two players) ===")

    poke_a = choose_pokemon(f"Player 1, choose your Pokemon")
    poke_b = choose_pokemon(f"Player 2, choose your Pokemon")

    participant_a = BattleParticipant(player_id="p1", name="Player 1", pokemon=poke_a)
    participant_b = BattleParticipant(player_id="p2", name="Player 2", pokemon=poke_b)

    battle = Battle(battle_id="room-1", player_a=participant_a, player_b=participant_b)
    show_state(battle)

    while not battle.is_finished():
        move_a = pick_move(participant_a)
        battle.submit_move("p1", move_a)

        move_b = pick_move(participant_b)
        battle.submit_move("p2", move_b)

        events = battle.resolve_turn()
        for event in events:
            print(f"> {event.message}")
        show_state(battle)

    winner = battle.participant_for(battle.winner)
    print(f"\n=== {winner.name} wins! ===")


if __name__ == "__main__":
    main()
