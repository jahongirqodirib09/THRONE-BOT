from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GamePhase(str, Enum):
    LOBBY = "lobby"
    NIGHT = "night"
    DAY = "day"
    VOTING = "voting"
    ENDED = "ended"


class PlayerStatus(str, Enum):
    ALIVE = "alive"
    DEAD = "dead"
    LEFT = "left"


@dataclass
class PlayerState:
    user_id: int
    name: str
    username: str | None = None

    role_key: str | None = None
    team: str | None = None

    status: PlayerStatus = PlayerStatus.ALIVE

    joined_at: float = 0.0
    last_activity: float = 0.0

    votes_received: int = 0
    voted: bool = False

    night_action_used: bool = False
    night_target: int | None = None

    final_words: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_alive(self) -> bool:
        return self.status == PlayerStatus.ALIVE

    @property
    def is_dead(self) -> bool:
        return self.status == PlayerStatus.DEAD

    @property
    def has_left(self) -> bool:
        return self.status == PlayerStatus.LEFT


@dataclass
class NightAction:
    actor_id: int
    action_type: str
    target_id: int | None = None

    priority: int = 0
    created_at: float = 0.0

    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class GameEvent:
    event_type: str
    message: str = ""

    player_id: int | None = None
    target_id: int | None = None

    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class VoteRecord:
    voter_id: int
    target_id: int | None

    created_at: float = 0.0


@dataclass
class GameState:
    chat_id: int

    phase: GamePhase = GamePhase.LOBBY

    players: dict[int, PlayerState] = field(default_factory=dict)

    votes: dict[int, VoteRecord] = field(default_factory=dict)

    night_actions: list[NightAction] = field(default_factory=list)

    events: list[GameEvent] = field(default_factory=list)

    day_number: int = 0
    night_number: int = 0

    phase_started_at: float = 0.0
    phase_ends_at: float = 0.0

    winner_team: str | None = None

    game_started: bool = False

    settings: dict[str, Any] = field(default_factory=dict)

    def add_player(
        self,
        user_id: int,
        name: str,
        username: str | None = None,
        joined_at: float = 0.0,
    ) -> PlayerState:
        if user_id in self.players:
            return self.players[user_id]

        player = PlayerState(
            user_id=user_id,
            name=name,
            username=username,
            joined_at=joined_at,
            last_activity=joined_at,
        )

        self.players[user_id] = player
        return player

    def remove_player(self, user_id: int) -> bool:
        player = self.players.get(user_id)

        if player is None:
            return False

        if player.status != PlayerStatus.ALIVE:
            return False

        player.status = PlayerStatus.LEFT
        return True

    def get_player(self, user_id: int) -> PlayerState | None:
        return self.players.get(user_id)

    def alive_players(self) -> list[PlayerState]:
        return [
            player
            for player in self.players.values()
            if player.is_alive
        ]

    def dead_players(self) -> list[PlayerState]:
        return [
            player
            for player in self.players.values()
            if player.is_dead
        ]

    def left_players(self) -> list[PlayerState]:
        return [
            player
            for player in self.players.values()
            if player.has_left
        ]

    def alive_count(self) -> int:
        return len(self.alive_players())

    def mark_dead(
        self,
        user_id: int,
        final_words: str | None = None,
    ) -> bool:
        player = self.players.get(user_id)

        if player is None or not player.is_alive:
            return False

        player.status = PlayerStatus.DEAD
        player.final_words = final_words

        return True

    def set_role(
        self,
        user_id: int,
        role_key: str,
        team: str,
    ) -> bool:
        player = self.players.get(user_id)

        if player is None:
            return False

        player.role_key = role_key
        player.team = team

        return True

    def get_team_players(
        self,
        team: str,
        alive_only: bool = False,
    ) -> list[PlayerState]:
        result = [
            player
            for player in self.players.values()
            if player.team == team
        ]

        if alive_only:
            result = [
                player
                for player in result
                if player.is_alive
            ]

        return result

    def get_teammates(
        self,
        user_id: int,
        alive_only: bool = True,
    ) -> list[PlayerState]:
        player = self.players.get(user_id)

        if player is None or player.team is None:
            return []

        teammates = self.get_team_players(
            player.team,
            alive_only=alive_only,
        )

        return [
            teammate
            for teammate in teammates
            if teammate.user_id != user_id
        ]

    def add_night_action(
        self,
        actor_id: int,
        action_type: str,
        target_id: int | None = None,
        priority: int = 0,
        created_at: float = 0.0,
        data: dict[str, Any] | None = None,
    ) -> NightAction:
        action = NightAction(
            actor_id=actor_id,
            action_type=action_type,
            target_id=target_id,
            priority=priority,
            created_at=created_at,
            data=data or {},
        )

        self.night_actions.append(action)

        player = self.players.get(actor_id)

        if player is not None:
            player.night_action_used = True
            player.night_target = target_id

        return action

    def get_actions_for_actor(
        self,
        actor_id: int,
    ) -> list[NightAction]:
        return [
            action
            for action in self.night_actions
            if action.actor_id == actor_id
        ]

    def get_actions_for_target(
        self,
        target_id: int,
    ) -> list[NightAction]:
        return [
            action
            for action in self.night_actions
            if action.target_id == target_id
        ]

    def clear_night_actions(self) -> None:
        self.night_actions.clear()

        for player in self.players.values():
            player.night_action_used = False
            player.night_target = None

    def add_event(
        self,
        event_type: str,
        message: str = "",
        player_id: int | None = None,
        target_id: int | None = None,
        data: dict[str, Any] | None = None,
    ) -> GameEvent:
        event = GameEvent(
            event_type=event_type,
            message=message,
            player_id=player_id,
            target_id=target_id,
            data=data or {},
        )

        self.events.append(event)
        return event

    def clear_events(self) -> None:
        self.events.clear()

    def register_vote(
        self,
        voter_id: int,
        target_id: int | None,
        created_at: float = 0.0,
    ) -> VoteRecord | None:
        voter = self.players.get(voter_id)

        if voter is None or not voter.is_alive:
            return None

        if self.phase != GamePhase.VOTING:
            return None

        old_vote = self.votes.get(voter_id)

        if old_vote is not None:
            old_target = old_vote.target_id

            if old_target is not None:
                old_player = self.players.get(old_target)

                if old_player is not None:
                    old_player.votes_received = max(
                        0,
                        old_player.votes_received - 1,
                    )

        if target_id is not None:
            target = self.players.get(target_id)

            if target is None or not target.is_alive:
                return None

        vote = VoteRecord(
            voter_id=voter_id,
            target_id=target_id,
            created_at=created_at,
        )

        self.votes[voter_id] = vote
        voter.voted = True

        if target_id is not None:
            target = self.players[target_id]
            target.votes_received += 1

        return vote

    def clear_votes(self) -> None:
        self.votes.clear()

        for player in self.players.values():
            player.votes_received = 0
            player.voted = False

    def vote_count(self) -> dict[int, int]:
        counts: dict[int, int] = {}

        for vote in self.votes.values():
            if vote.target_id is None:
                continue

            counts[vote.target_id] = (
                counts.get(vote.target_id, 0) + 1
            )

        return counts

    def voting_result(self) -> int | None:
        counts = self.vote_count()

        if not counts:
            return None

        highest = max(counts.values())

        winners = [
            player_id
            for player_id, count in counts.items()
            if count == highest
        ]

        if len(winners) != 1:
            return None

        return winners[0]

    def all_alive_have_voted(self) -> bool:
        alive = self.alive_players()

        if not alive:
            return False

        return all(
            player.user_id in self.votes
            for player in alive
        )

    def start_game(self, started_at: float = 0.0) -> None:
        self.phase = GamePhase.NIGHT
        self.game_started = True
        self.night_number = 1
        self.day_number = 0
        self.phase_started_at = started_at

        self.clear_votes()
        self.clear_night_actions()
        self.clear_events()

    def start_night(
        self,
        started_at: float = 0.0,
        ends_at: float = 0.0,
    ) -> None:
        self.phase = GamePhase.NIGHT
        self.night_number += 1
        self.phase_started_at = started_at
        self.phase_ends_at = ends_at

        self.clear_votes()
        self.clear_night_actions()
        self.clear_events()

    def start_day(
        self,
        started_at: float = 0.0,
        ends_at: float = 0.0,
    ) -> None:
        self.phase = GamePhase.DAY
        self.day_number += 1
        self.phase_started_at = started_at
        self.phase_ends_at = ends_at

        self.clear_votes()

    def start_voting(
        self,
        started_at: float = 0.0,
        ends_at: float = 0.0,
    ) -> None:
        self.phase = GamePhase.VOTING
        self.phase_started_at = started_at
        self.phase_ends_at = ends_at

        self.clear_votes()

    def end_game(self, winner_team: str | None = None) -> None:
        self.phase = GamePhase.ENDED
        self.winner_team = winner_team
        self.game_started = False

    def reset(self) -> None:
        self.phase = GamePhase.LOBBY

        self.players.clear()
        self.votes.clear()
        self.night_actions.clear()
        self.events.clear()

        self.day_number = 0
        self.night_number = 0

        self.phase_started_at = 0.0
        self.phase_ends_at = 0.0

        self.winner_team = None
        self.game_started = False

    def player_names(
        self,
        alive_only: bool = False,
    ) -> list[str]:
        players = (
            self.alive_players()
            if alive_only
            else list(self.players.values())
        )

        return [
            player.name
            for player in players
        ]

    def summary(self) -> dict[str, Any]:
        return {
            "chat_id": self.chat_id,
            "phase": self.phase.value,
            "players": len(self.players),
            "alive": self.alive_count(),
            "dead": len(self.dead_players()),
            "left": len(self.left_players()),
            "day": self.day_number,
            "night": self.night_number,
            "winner": self.winner_team,
            "started": self.game_started,
        }
