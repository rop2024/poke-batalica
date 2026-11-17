from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from damage import calculate_damage, type_effectiveness
from pokemon import Move, PokemonSpecies


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
class Battle:
    battle_id: str
    player_a: BattleParticipant
    player_b: BattleParticipant
    turn: int = 0
    finished: bool = False
    winner: Optional[str] = None
    events: List[BattleEvent] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def is_finished(self) -> bool:
        return self.finished

    def get_events(self) -> List[BattleEvent]:
        return list(self.events)

    def participant_for(self, player_id: str) -> Optional[BattleParticipant]:
        if self.player_a.player_id == player_id:
            return self.player_a
        if self.player_b.player_id == player_id:
            return self.player_b
        return None

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def submit_move(self, player_id: str, move_name: str) -> BattleEvent:
        if self.finished:
            return self._add_event(type="error", message="battle is already finished")

        participant = self.participant_for(player_id)
        if participant is None:
            return self._add_event(type="error", message=f"player {player_id} is not in this battle")

        if participant.submitted_move is not None:
            return self._add_event(type="error", message=f"{participant.name} already submitted a move this turn")

        if participant.pokemon.fainted:
            return self._add_event(
                type="error",
                message=f"{participant.name}'s {participant.pokemon.species.name} has fainted",
            )

        pokemon = participant.pokemon.species
        move = next((m for m in pokemon.moves if m.name.lower() == move_name.lower()), None)
        if move is None:
            return self._add_event(type="error", message=f"{pokemon.name} does not know the move '{move_name}'")

        participant.submitted_move = move
        return self._add_event(
            type="move_submitted",
            actor=participant.name,
            move=move.name,
            message=f"{participant.name} selected {move.name}",
        )

    def resolve_turn(self) -> List[BattleEvent]:
        if self.finished:
            return [self._add_event(type="error", message="battle already finished")]

        if self.player_a.submitted_move is None or self.player_b.submitted_move is None:
            return [self._add_event(
                type="error",
                message="both players must submit a move before the turn can resolve",
            )]

        self.turn += 1
        events: List[BattleEvent] = [self._add_event(type="turn_started", turn=self.turn,
                                                     message=f"turn {self.turn} begins")]

        first, second = self._order_participants()

        events.extend(self._execute_attack(first, second))
        if self._fainted(second):
            self._finish(first.player_id, events)
            return events

        events.extend(self._execute_attack(second, first))
        if self._fainted(first):
            self._finish(second.player_id, events)
            return events

        # Turn complete: clear submissions for the next round
        self.player_a.submitted_move = None
        self.player_b.submitted_move = None

        events.append(self._add_event(type="turn_resolved", turn=self.turn,
                                      message=f"turn {self.turn} resolved"))
        return events

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _add_event(self, **kwargs) -> BattleEvent:
        event = BattleEvent(turn=kwargs.pop("turn", self.turn), **kwargs)
        self.events.append(event)
        return event

    def _order_participants(self) -> Tuple[BattleParticipant, BattleParticipant]:
        """Faster Pokemon attacks first. Tie goes to player_a."""
        speed_a = self.player_a.pokemon.species.base_speed
        speed_b = self.player_b.pokemon.species.base_speed
        if speed_b > speed_a:
            return self.player_b, self.player_a
        return self.player_a, self.player_b

    def _execute_attack(self, attacker: BattleParticipant, defender: BattleParticipant) -> List[BattleEvent]:
        events: List[BattleEvent] = []
        move = attacker.submitted_move
        if move is None:
            return events

        species = attacker.pokemon.species
        target_species = defender.pokemon.species

        damage = calculate_damage(move, species, target_species)
        effectiveness = type_effectiveness(move.move_type, target_species.types)

        defender.pokemon.current_hp = max(0, defender.pokemon.current_hp - damage)
        if defender.pokemon.current_hp <= 0:
            defender.pokemon.current_hp = 0
            defender.pokemon.fainted = True

        events.append(self._add_event(
            type="attack",
            actor=attacker.name,
            target=defender.name,
            move=move.name,
            damage=damage,
            effectiveness=effectiveness,
            hp=defender.pokemon.current_hp,
            max_hp=defender.pokemon.max_hp,
            message=f"{species.name} used {move.name} on {target_species.name} for {damage} damage",
        ))

        if defender.pokemon.fainted:
            events.append(self._add_event(
                type="faint",
                actor=defender.name,
                target=defender.name,
                message=f"{target_species.name} fainted!",
            ))

        return events

    def _fainted(self, participant: BattleParticipant) -> bool:
        return participant.pokemon.fainted

    def _finish(self, winner_player_id: str, events: List[BattleEvent]) -> None:
        self.finished = True
        winner = self.participant_for(winner_player_id)
        self.winner = winner_player_id
        events.append(self._add_event(
            type="battle_finished",
            winner=winner_player_id,
            message=f"{winner.name if winner else winner_player_id} wins the battle!",
        ))
