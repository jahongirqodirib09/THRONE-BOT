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


@dataclass
class PlayerState:
    user_id: int
    username: str | None = None
    first_name: str = ""

    role_id: str | None = None
    team: str | None = None

    alive: bool = True
    joined: bool = True

    voted_for: int | None = None

    night_action_used: bool = False
    day_message_sent: bool = False

    inactivity_count: int = 0

    protection_used: bool = False
    escape_used: bool = False

    temporary_data: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class GameState:
    chat_id: int

    phase: GamePhase = GamePhase.LOBBY

    players: dict[int, PlayerState] = field(
        default_factory=dict
    )

    phase_started_at: float | None = None
    phase_ends_at: float | None = None

    countdown_started: bool = False
    finished: bool = False

    votes: dict[int, int] = field(
        default_factory=dict
    )

    night_actions: dict[int, dict[str, Any]] = field(
        default_factory=dict
    )

    events: list[dict[str, Any]] = field(
        default_factory=list
    )

    winner_team: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def add_player(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str = "",
    ) -> bool:
        if self.finished:
            return False

        if user_id in self.players:
            player = self.players[user_id]

            if username is not None:
                player.username = username

            if first_name:
                player.first_name = first_name

            player.joined = True
            return False

        self.players[user_id] = PlayerState(
            user_id=user_id,
            username=username,
            first_name=first_name,
        )

        return True

    def remove_player(self, user_id: int) -> bool:
        if user_id not in self.players:
            return False

        del self.players[user_id]
        self.votes.pop(user_id, None)
        self.night_actions.pop(user_id, None)

        return True

    def get_player(
        self,
        user_id: int,
    ) -> PlayerState | None:
        return self.players.get(user_id)

    def alive_players(self) -> list[PlayerState]:
        return [
            player
            for player in self.players.values()
            if player.alive and player.joined
        ]

    def dead_players(self) -> list[PlayerState]:
        return [
            player
            for player in self.players.values()
            if not player.alive
        ]

    def joined_players(self) -> list[PlayerState]:
        return [
            player
            for player in self.players.values()
            if player.joined
        ]

    def player_count(self) -> int:
        return len(self.joined_players())

    def alive_count(self) -> int:
        return len(self.alive_players())

    def kill_player(
        self,
        user_id: int,
    ) -> bool:
        player = self.get_player(user_id)

        if player is None or not player.alive:
            return False

        player.alive = False
        player.voted_for = None

        return True

    def revive_player(
        self,
        user_id: int,
    ) -> bool:
        player = self.get_player(user_id)

        if player is None or player.alive:
            return False

        player.alive = True

        return True

    def set_role(
        self,
        user_id: int,
        role_id: str,
        team: str,
    ) -> bool:
        player = self.get_player(user_id)

        if player is None:
            return False

        player.role_id = role_id
        player.team = team

        return True

    def reset_votes(self) -> None:
        self.votes.clear()

        for player in self.players.values():
            player.voted_for = None

    def add_vote(
        self,
        voter_id: int,
        target_id: int,
    ) -> bool:
        if self.phase != GamePhase.VOTING:
            return False

        voter = self.get_player(voter_id)
        target = self.get_player(target_id)

        if voter is None or target is None:
            return False

        if not voter.alive or not target.alive:
            return False

        self.votes[voter_id] = target_id
        voter.voted_for = target_id

        return True

    def vote_counts(self) -> dict[int, int]:
        counts: dict[int, int] = {}

        for target_id in self.votes.values():
            target = self.get_player(target_id)

            if target is None or not target.alive:
                continue

            counts[target_id] = (
                counts.get(target_id, 0) + 1
            )

        return counts

    def most_voted_player(self) -> int | None:
        counts = self.vote_counts()

        if not counts:
            return None

        highest = max(counts.values())

        winners = [
            user_id
            for user_id, count in counts.items()
            if count == highest
        ]

        if len(winners) != 1:
            return None

        return winners[0]

    def set_phase(
        self,
        phase: GamePhase,
        started_at: float | None = None,
        ends_at: float | None = None,
    ) -> None:
        self.phase = phase
        self.phase_started_at = started_at
        self.phase_ends_at = ends_at

        if phase != GamePhase.VOTING:
            self.reset_votes()

        if phase != GamePhase.NIGHT:
            self.night_actions.clear()

    def set_night_action(
        self,
        user_id: int,
        action: dict[str, Any],
    ) -> bool:
        if self.phase != GamePhase.NIGHT:
            return False

        player = self.get_player(user_id)

        if player is None or not player.alive:
            return False

        self.night_actions[user_id] = action
        player.night_action_used = True

        return True

    def get_night_action(
        self,
        user_id: int,
    ) -> dict[str, Any] | None:
        return self.night_actions.get(user_id)

    def add_event(
        self,
        event_type: str,
        **data: Any,
    ) -> None:
        self.events.append(
            {
                "type": event_type,
                **data,
            }
        )

    def clear_events(self) -> None:
        self.events.clear()

    def reset_night_actions(self) -> None:
        self.night_actions.clear()

        for player in self.players.values():
            player.night_action_used = False

    def reset_day_actions(self) -> None:
        for player in self.players.values():
            player.day_message_sent = False

    def mark_inactive(
        self,
        user_id: int,
    ) -> bool:
        player = self.get_player(user_id)

        if player is None:
            return False

        player.inactivity_count += 1

        return True

    def reset_inactivity(
        self,
        user_id: int,
    ) -> bool:
        player = self.get_player(user_id)

        if player is None:
            return False

        player.inactivity_count = 0

        return True

    def set_winner(
        self,
        team: str,
    ) -> None:
        self.winner_team = team
        self.finished = True
        self.phase = GamePhase.ENDED

    def reset_for_new_game(self) -> None:
        self.phase = GamePhase.LOBBY
        self.phase_started_at = None
        self.phase_ends_at = None

        self.players.clear()
        self.votes.clear()
        self.night_actions.clear()
        self.events.clear()

        self.winner_team = None
        self.finished = False
        self.countdown_started = False
        self.metadata.clear()
