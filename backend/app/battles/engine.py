import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

# --- Type effectiveness chart ---

TYPE_CHART: Dict[str, Dict[str, float]] = {
    "normal": {"rock": 0.5, "ghost": 0.0, "steel": 0.5},
    "fire": {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 2.0, "bug": 2.0,
             "rock": 0.5, "dragon": 0.5, "steel": 2.0},
    "water": {"fire": 2.0, "water": 0.5, "grass": 0.5, "ground": 2.0,
              "rock": 2.0, "dragon": 0.5},
    "electric": {"water": 2.0, "electric": 0.5, "grass": 0.5, "ground": 0.0,
                 "flying": 2.0, "dragon": 0.5},
    "grass": {"fire": 0.5, "water": 2.0, "grass": 0.5, "poison": 0.5,
              "ground": 2.0, "flying": 0.5, "bug": 0.5, "rock": 2.0,
              "dragon": 0.5, "steel": 0.5},
    "ice": {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 0.5, "ground": 2.0,
            "flying": 2.0, "dragon": 2.0, "steel": 0.5},
    "fighting": {"normal": 2.0, "ice": 2.0, "poison": 0.5, "flying": 0.5,
                 "psychic": 0.5, "bug": 0.5, "rock": 2.0, "ghost": 0.0,
                 "dark": 2.0, "steel": 2.0, "fairy": 0.5},
    "poison": {"grass": 2.0, "poison": 0.5, "ground": 0.5, "rock": 0.5,
               "ghost": 0.5, "steel": 0.0, "fairy": 2.0},
    "ground": {"fire": 2.0, "electric": 2.0, "grass": 0.5, "poison": 2.0,
               "flying": 0.0, "bug": 0.5, "rock": 2.0, "steel": 2.0},
    "flying": {"electric": 0.5, "grass": 2.0, "ice": 0.5, "fighting": 2.0,
               "bug": 2.0, "rock": 0.5, "steel": 0.5},
    "psychic": {"fighting": 2.0, "poison": 2.0, "psychic": 0.5, "dark": 0.0,
                "steel": 0.5},
    "bug": {"fire": 0.5, "grass": 2.0, "fighting": 0.5, "poison": 0.5,
            "flying": 0.5, "psychic": 2.0, "ghost": 0.5, "dark": 2.0,
            "steel": 0.5, "fairy": 0.5},
    "rock": {"fire": 2.0, "ice": 2.0, "fighting": 0.5, "ground": 0.5,
             "flying": 2.0, "bug": 2.0, "steel": 0.5},
    "ghost": {"normal": 0.0, "ghost": 2.0, "psychic": 2.0, "dark": 0.5},
    "dragon": {"dragon": 2.0, "steel": 0.5, "fairy": 0.0},
    "dark": {"fighting": 0.5, "psychic": 2.0, "ghost": 2.0, "dark": 0.5,
             "fairy": 0.5},
    "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2.0,
              "rock": 2.0, "steel": 0.5, "fairy": 2.0},
    "fairy": {"fire": 0.5, "fighting": 2.0, "poison": 0.5, "ground": 0.5,
              "dragon": 2.0, "dark": 2.0, "steel": 0.5},
}

DEFAULT_LEVEL = 50
RANDOM_MIN = 0.85
RANDOM_MAX = 1.0


def type_effectiveness(move_type: str, defender_types: Tuple[str, ...]) -> float:
    multiplier = 1.0
    chart = TYPE_CHART.get(move_type, {})
    for defender_type in defender_types:
        multiplier *= chart.get(defender_type, 1.0)
    return multiplier


def calculate_damage(
    power: int,
    attack: int,
    defense: int,
    move_type: str,
    defender_types: Tuple[str, ...],
    level: int = DEFAULT_LEVEL,
    random_factor: Optional[float] = None,
) -> int:
    if power is None or power <= 0:
        return 0
    if random_factor is None:
        random_factor = random.uniform(RANDOM_MIN, RANDOM_MAX)
    base = (((2 * level / 5 + 2) * power * attack / defense) / 50) + 2
    effectiveness = type_effectiveness(move_type, defender_types)
    if effectiveness <= 0:
        return 0
    damage = base * effectiveness * random_factor
    return max(1, int(damage))


# --- Domain objects ---


@dataclass
class Move:
    name: str
    power: Optional[int]
    move_type: str
    accuracy: Optional[int]
    pp: int


@dataclass
class PokemonSpecies:
    pokemon_id: int
    name: str
    types: Tuple[str, ...]
    base_hp: int
    base_attack: int
    base_defense: int
    base_special_attack: int
    base_special_defense: int
    base_speed: int
    sprite_url: Optional[str]
    official_artwork_url: Optional[str]
    cry_url: Optional[str]
    moves: List[Move] = field(default_factory=list)


@dataclass
class BattlePokemon:
    species: PokemonSpecies
    current_hp: int
    max_hp: int
    fainted: bool = False

    @property
    def hp_percent(self) -> float:
        if self.max_hp <= 0:
            return 0.0
        return max(0, self.current_hp) / self.max_hp


@dataclass
class BattleParticipant:
    player_id: str
    name: str
    pokemon: BattlePokemon
    submitted_move: Optional[Move] = None


@dataclass
class BattleEvent:
    turn: int
    type: str
    actor: Optional[str] = None
    target: Optional[str] = None
    move: Optional[str] = None
    damage: Optional[int] = None
    effectiveness: Optional[float] = None
    random_factor: Optional[float] = None
    hp: Optional[int] = None
    max_hp: Optional[int] = None
    winner: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "turn": self.turn,
            "type": self.type,
            "actor": self.actor,
            "target": self.target,
            "move": self.move,
            "damage": self.damage,
            "effectiveness": self.effectiveness,
            "random_factor": self.random_factor,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "winner": self.winner,
            "message": self.message,
        }


class Battle:
    def __init__(self, battle_id: str, player_a: BattleParticipant, player_b: BattleParticipant):
        self.battle_id = battle_id
        self.player_a = player_a
        self.player_b = player_b
        self.turn = 0
        self.finished = False
        self.winner: Optional[str] = None
        self.events: List[BattleEvent] = []

    # -- query --
    def is_finished(self) -> bool:
        return self.finished

    def get_events(self) -> List[dict]:
        return [e.to_dict() for e in self.events]

    def participant_for(self, player_id: str) -> Optional[BattleParticipant]:
        if self.player_a.player_id == player_id:
            return self.player_a
        if self.player_b.player_id == player_id:
            return self.player_b
        return None

    # -- actions --
    def submit_move(self, player_id: str, move_name: str) -> dict:
        if self.finished:
            return self._add_event("error", message="battle is already finished").to_dict()

        participant = self.participant_for(player_id)
        if participant is None:
            return self._add_event("error", message=f"player {player_id} is not in this battle").to_dict()

        if participant.submitted_move is not None:
            return self._add_event("error", message=f"{participant.name} already submitted a move this turn").to_dict()

        if participant.pokemon.fainted:
            return self._add_event(
                "error",
                message=f"{participant.name}'s {participant.pokemon.species.name} has fainted",
            ).to_dict()

        move = next((m for m in participant.pokemon.species.moves if m.name.lower() == move_name.lower()), None)
        if move is None:
            return self._add_event("error", message=f"{participant.pokemon.species.name} does not know '{move_name}'").to_dict()

        participant.submitted_move = move
        return self._add_event("move_submitted", actor=participant.name, move=move.name,
                               message=f"{participant.name} selected {move.name}").to_dict()

    def resolve_turn(self) -> List[dict]:
        if self.finished:
            return [self._add_event("error", message="battle already finished").to_dict()]

        if self.player_a.submitted_move is None or self.player_b.submitted_move is None:
            return [self._add_event(
                "error", message="both players must submit a move before the turn can resolve",
            ).to_dict()]

        self.turn += 1
        events: List[dict] = [self._add_event("turn_started", turn=self.turn,
                                              message=f"turn {self.turn} begins").to_dict()]

        first, second = self._order_participants()

        events.extend(self._execute_attack(first, second))
        if self._fainted(second):
            self._finish(first.player_id, events)
            return events

        events.extend(self._execute_attack(second, first))
        if self._fainted(first):
            self._finish(second.player_id, events)
            return events

        self.player_a.submitted_move = None
        self.player_b.submitted_move = None

        events.append(self._add_event("turn_resolved", turn=self.turn,
                                      message=f"turn {self.turn} resolved").to_dict())
        return events

    # -- internal --
    def _add_event(self, etype: str, **kwargs) -> BattleEvent:
        event = BattleEvent(turn=kwargs.pop("turn", self.turn), type=etype, **kwargs)
        self.events.append(event)
        return event

    def _order_participants(self) -> Tuple[BattleParticipant, BattleParticipant]:
        speed_a = self.player_a.pokemon.species.base_speed
        speed_b = self.player_b.pokemon.species.base_speed
        if speed_b > speed_a:
            return self.player_b, self.player_a
        return self.player_a, self.player_b

    def _execute_attack(self, attacker: BattleParticipant, defender: BattleParticipant) -> List[dict]:
        events: List[dict] = []
        move = attacker.submitted_move
        if move is None:
            return events

        species = attacker.pokemon.species
        target_species = defender.pokemon.species

        damage = calculate_damage(
            power=move.power or 0,
            attack=species.base_attack,
            defense=target_species.base_defense,
            move_type=move.move_type,
            defender_types=target_species.types,
        )
        effectiveness = type_effectiveness(move.move_type, target_species.types)

        defender.pokemon.current_hp = max(0, defender.pokemon.current_hp - damage)
        if defender.pokemon.current_hp <= 0:
            defender.pokemon.current_hp = 0
            defender.pokemon.fainted = True

        events.append(self._add_event(
            "attack",
            actor=attacker.name,
            target=defender.name,
            move=move.name,
            damage=damage,
            effectiveness=effectiveness,
            hp=defender.pokemon.current_hp,
            max_hp=defender.pokemon.max_hp,
            message=f"{species.name} used {move.name} on {target_species.name} for {damage} damage",
        ).to_dict())

        if defender.pokemon.fainted:
            events.append(self._add_event(
                "faint",
                actor=defender.name,
                target=defender.name,
                message=f"{target_species.name} fainted!",
            ).to_dict())

        return events

    def _fainted(self, participant: BattleParticipant) -> bool:
        return participant.pokemon.fainted

    def _finish(self, winner_player_id: str, events: List[dict]) -> None:
        self.finished = True
        self.winner = winner_player_id
        winner = self.participant_for(winner_player_id)
        events.append(self._add_event(
            "battle_finished",
            winner=winner_player_id,
            message=f"{winner.name if winner else winner_player_id} wins the battle!",
        ).to_dict())
