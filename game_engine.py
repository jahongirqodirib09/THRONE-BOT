from __future__ import annotations

import random
import time
from collections import Counter
from dataclasses import dataclass
from typing import Any

from config import MAX_PLAYERS, MIN_PLAYERS
from game_state import (
    GameEvent,
    GamePhase,
    GameState,
    NightAction,
    PlayerState,
    PlayerStatus,
)
from roles import ROLE_MAP, TEAM_LABELS


@dataclass
class ActionResult:
    success: bool
    message: str = ""
    data: dict[str, Any] | None = None


class GameEngine:
    """
    THRONE o'yinining asosiy boshqaruv qatlami.

    Bu klass:
    - lobby
    - o'yin boshlanishi
    - rol taqsimlash
    - jamoa/sheriklar
    - tun harakatlari
    - ovoz berish
    - o'lim
    - g'olibni aniqlash
    - o'yin yakuni

    bilan ishlaydi.
    """

    def __init__(self) -> None:
        self.games: dict[int, GameState] = {}

    # ============================================================
    # GAME / LOBBY
    # ============================================================

    def create_game(self, chat_id: int) -> GameState:
        game = self.games.get(chat_id)

        if game is not None:
            return game

        game = GameState(chat_id=chat_id)
        self.games[chat_id] = game

        return game

    def get_game(self, chat_id: int) -> GameState | None:
        return self.games.get(chat_id)

    def get_or_create_game(self, chat_id: int) -> GameState:
        return self.games.setdefault(
            chat_id,
            GameState(chat_id=chat_id),
        )

    def remove_game(self, chat_id: int) -> None:
        self.games.pop(chat_id, None)

    def add_player(
        self,
        chat_id: int,
        user_id: int,
        name: str,
        username: str | None = None,
    ) -> ActionResult:
        game = self.get_or_create_game(chat_id)

        if game.phase != GamePhase.LOBBY:
            return ActionResult(
                False,
                "⚠️ Hozir yangi o‘yinchilar qabul qilinmaydi.",
            )

        if user_id in game.players:
            return ActionResult(
                False,
                "ℹ️ Siz allaqachon o‘yinga qo‘shilgansiz.",
            )

        if len(game.players) >= MAX_PLAYERS:
            return ActionResult(
                False,
                f"⚠️ O‘yinchilar soni {MAX_PLAYERS} nafarga yetdi.",
            )

        now = time.time()

        player = game.add_player(
            user_id=user_id,
            name=name,
            username=username,
            joined_at=now,
        )

        player.last_activity = now

        return ActionResult(
            True,
            f"👤 {name} o‘yinga qo‘shildi.",
            {"player": player},
        )

    def remove_player(
        self,
        chat_id: int,
        user_id: int,
    ) -> ActionResult:
        game = self.get_game(chat_id)

        if game is None:
            return ActionResult(
                False,
                "⚠️ Faol o‘yin topilmadi.",
            )

        player = game.get_player(user_id)

        if player is None:
            return ActionResult(
                False,
                "⚠️ Siz o‘yinda emassiz.",
            )

        if game.phase != GamePhase.LOBBY:
            return ActionResult(
                False,
                "⚠️ O‘yin boshlanganidan keyin lobbydan chiqib bo‘lmaydi.",
            )

        player.status = PlayerStatus.LEFT

        return ActionResult(
            True,
            f"🚪 {player.name} o‘yindan chiqdi.",
        )

    def can_start(self, chat_id: int) -> ActionResult:
        game = self.get_game(chat_id)

        if game is None:
            return ActionResult(
                False,
                "⚠️ O‘yin yaratilmagan.",
            )

        if game.phase != GamePhase.LOBBY:
            return ActionResult(
                False,
                "⚠️ O‘yin allaqachon boshlangan.",
            )

        count = game.alive_count()

        if count < MIN_PLAYERS:
            return ActionResult(
                False,
                f"⚠️ O‘yinni boshlash uchun kamida "
                f"{MIN_PLAYERS} nafar o‘yinchi kerak.\n"
                f"👥 Hozir: {count}",
            )

        return ActionResult(
            True,
            f"✅ O‘yinni boshlash mumkin.\n👥 O‘yinchilar: {count}",
        )

    # ============================================================
    # ROLE ASSIGNMENT
    # ============================================================

    def start_game(
        self,
        chat_id: int,
    ) -> ActionResult:
        check = self.can_start(chat_id)

        if not check.success:
            return check

        game = self.get_game(chat_id)

        if game is None:
            return ActionResult(
                False,
                "⚠️ O‘yin topilmadi.",
            )

        players = game.alive_players()

        self._assign_roles(players)

        game.start_game(started_at=time.time())

        event = game.add_event(
            event_type="game_started",
            message="👑 THRONE: Taxtlar O‘yini boshlandi.",
        )

        return ActionResult(
            True,
            event.message,
            {
                "players": players,
                "event": event,
            },
        )

    def _assign_roles(
        self,
        players: list[PlayerState],
    ) -> None:
        """
        O‘yinchi soniga qarab rollarni tanlaydi.

        36 tagacha rol mavjud.
        Kam o‘yinchida barcha rollar ishlatilmaydi.

        Asosiy prinsip:
        - barcha jamoalardan rollar bo‘ladi;
        - juda kuchli rollar kichik o‘yinda haddan tashqari ko‘paymaydi;
        - rollar tasodifiy taqsimlanadi.
        """

        count = len(players)

        role_keys = self._build_role_pool(count)

        random.shuffle(players)
        random.shuffle(role_keys)

        for player, role_key in zip(players, role_keys):
            role = ROLE_MAP[role_key]

            game_team = self._get_role_team(role)

            player.role_key = role_key
            player.team = game_team

    def _build_role_pool(
        self,
        player_count: int,
    ) -> list[str]:
        all_keys = list(ROLE_MAP.keys())

        if player_count >= len(all_keys):
            return all_keys.copy()

        ordinary = [
            "tinch_aholi",
            "xizmatkor",
            "aygoqchi",
            "qorovul",
            "kuzatuvchi",
            "solnomachi",
            "savdogar",
            "tabib",
            "oshpaz",
        ]

        crown = [
            "shoh",
            "malika",
            "shahzoda",
            "vazir",
            "bosh_qomondon",
            "qirol_qoriqchisi",
            "qozi",
            "xazinachi",
            "ritsar",
        ]

        shadow = [
            "soya_boshligi",
            "qotil",
            "josus",
            "soxta_maslahatchi",
            "xoin",
            "qora_vazir",
            "dushman_qiroli",
            "dushman_qomondoni",
            "dushman_josusi",
            "dushman_suiqasdchisi",
        ]

        solo = [
            "ovchi",
            "telba",
            "sayyoh",
            "yollanma_jangchi",
            "surgun_shahzoda",
            "taxt_davogari",
            "qaroqchi",
        ]

        legion = [
            "tabib",
            "kuzatuvchi",
            "qorovul",
            "solnomachi",
            "savdogar",
            "suiqasdchi",
            "oshpaz",
        ]

        guaranteed: list[str] = []

        # Kichik o‘yinda Crown asos bo‘ladi.
        guaranteed.extend(
            random.sample(
                crown,
                min(2, len(crown)),
            )
        )

        # Soya albatta bo‘ladi.
        guaranteed.extend(
            random.sample(
                shadow,
                min(1, len(shadow)),
            )
        )

        # Legiondan kamida bitta.
        guaranteed.extend(
            random.sample(
                legion,
                min(1, len(legion)),
            )
        )

        # 4 o‘yinchida kamida bitta yakka rol.
        if player_count >= 4:
            guaranteed.extend(
                random.sample(
                    solo,
                    min(1, len(solo)),
                )
            )

        guaranteed = list(dict.fromkeys(guaranteed))

        # Juda katta bo‘lsa kesamiz.
        guaranteed = guaranteed[:player_count]

        remaining = player_count - len(guaranteed)

        candidates = [
            role_key
            for role_key in all_keys
            if role_key not in guaranteed
        ]

        # Kichik o‘yinda haddan tashqari kuchli rollarni
        # kamroq tanlashga harakat qilamiz.
        if player_count <= 6:
            candidates = [
                key
                for key in candidates
                if key not in {
                    "dushman_qiroli",
                    "dushman_qomondoni",
                    "dushman_suiqasdchisi",
                    "taxt_davogari",
                }
            ]

        random.shuffle(candidates)

        pool = guaranteed + candidates[:remaining]

        # Xavfsizlik tekshiruvi.
        pool = [
            key
            for key in pool
            if key in ROLE_MAP
        ]

        if len(pool) < player_count:
            fallback = [
                key
                for key in all_keys
                if key not in pool
            ]

            pool.extend(
                fallback[:player_count - len(pool)]
            )

        return pool[:player_count]

    @staticmethod
    def _get_role_team(role: Any) -> str:
        team = getattr(role, "team", None)

        if team:
            return team

        # roles.py tuzilmasi team o‘rniga boshqa nom ishlatsa,
        # quyidagi fallback ishlaydi.
        role_key = getattr(role, "key", "")

        if role_key in {
            "shoh",
            "malika",
            "shahzoda",
            "vazir",
            "bosh_qomondon",
            "qirol_qoriqchisi",
            "qozi",
            "xazinachi",
            "ritsar",
            "xizmatkor",
            "tinch_aholi",
            "aygoqchi",
        }:
            return "kron"

        if role_key in {
            "soya_boshligi",
            "qotil",
            "josus",
            "soxta_maslahatchi",
            "xoin",
            "qora_vazir",
            "dushman_qiroli",
            "dushman_qomondoni",
            "dushman_josusi",
            "dushman_suiqasdchisi",
        }:
            return "soya"

        if role_key in {
            "ovchi",
            "telba",
            "sayyoh",
            "yollanma_jangchi",
            "surgun_shahzoda",
            "taxt_davogari",
            "qaroqchi",
        }:
            return "yakka"

        return "legion"

    # ============================================================
    # PLAYER / ROLE INFORMATION
    # ============================================================

    def get_player(
        self,
        chat_id: int,
        user_id: int,
    ) -> PlayerState | None:
        game = self.get_game(chat_id)

        if game is None:
            return None

        return game.get_player(user_id)

    def get_role_key(
        self,
        chat_id: int,
        user_id: int,
    ) -> str | None:
        player = self.get_player(chat_id, user_id)

        if player is None:
            return None

        return player.role_key

    def get_role(
        self,
        chat_id: int,
        user_id: int,
    ) -> Any | None:
        role_key = self.get_role_key(
            chat_id,
            user_id,
        )

        if role_key is None:
            return None

        return ROLE_MAP.get(role_key)

    def get_teammates(
        self,
        chat_id: int,
        user_id: int,
    ) -> list[PlayerState]:
        game = self.get_game(chat_id)

        if game is None:
            return []

        return game.get_teammates(
            user_id,
            alive_only=True,
        )

    def teammate_names(
        self,
        chat_id: int,
        user_id: int,
    ) -> list[str]:
        return [
            player.name
            for player in self.get_teammates(
                chat_id,
                user_id,
            )
        ]

    # ============================================================
    # PHASES
    # ============================================================

    def start_night(
        self,
        chat_id: int,
        duration: int = 60,
    ) -> ActionResult:
        game = self.get_game(chat_id)

        if game is None:
            return ActionResult(
                False,
                "⚠️ O‘yin topilmadi.",
            )

        if not game.game_started:
            return ActionResult(
                False,
                "⚠️ O‘yin hali boshlanmagan.",
            )

        now = time.time()

        game.start_night(
            started_at=now,
            ends_at=now + duration,
        )

        return ActionResult(
            True,
            "🌙 THRONE: Tun boshlandi.",
        )

    def start_day(
        self,
        chat_id: int,
        duration: int = 45,
    ) -> ActionResult:
        game = self.get_game(chat_id)

        if game is None:
            return ActionResult(
                False,
                "⚠️ O‘yin topilmadi.",
            )

        now = time.time()

        game.start_day(
            started_at=now,
            ends_at=now + duration,
        )

        return ActionResult(
            True,
            f"☀️ THRONE: {game.day_number}-kun boshlandi.",
        )

    def start_voting(
        self,
        chat_id: int,
        duration: int = 45,
    ) -> ActionResult:
        game = self.get_game(chat_id)

        if game is None:
            return ActionResult(
                False,
                "⚠️ O‘yin topilmadi.",
            )

        now = time.time()

        game.start_voting(
            started_at=now,
            ends_at=now + duration,
        )

        return ActionResult(
            True,
            "🗳️ THRONE: Ovoz berish boshlandi.",
        )

    # ============================================================
    # ACTIVITY
    # ============================================================

    def update_activity(
        self,
        chat_id: int,
        user_id: int,
    ) -> bool:
        player = self.get_player(
            chat_id,
            user_id,
        )

        if player is None:
            return False

        if not player.is_alive:
            return False

        player.last_activity = time.time()

        return True

    # ============================================================
    # NIGHT ACTIONS
    # ============================================================

    def submit_night_action(
        self,
        chat_id: int,
        actor_id: int,
        action_type: str,
        target_id: int | None = None,
        priority: int = 0,
        data: dict[str, Any] | None = None,
    ) -> ActionResult:
        game = self.get_game(chat_id)

        if game is None:
            return ActionResult(
                False,
                "⚠️ O‘yin topilmadi.",
            )

        if game.phase != GamePhase.NIGHT:
            return ActionResult(
                False,
                "🌙 Hozir tun bosqichi emas.",
            )

        actor = game.get_player(actor_id)

        if actor is None or not actor.is_alive:
            return ActionResult(
                False,
                "⚠️ Siz bu harakatni bajara olmaysiz.",
            )

        if target_id is not None:
            target = game.get_player(target_id)

            if target is None or not target.is_alive:
                return ActionResult(
                    False,
                    "⚠️ Tanlangan o‘yinchi faol emas.",
                )

            if target_id == actor_id:
                # Ayrim maxsus rollar keyinchalik o‘ziga
                # nishon tanlashi mumkin.
                if action_type not in {
                    "self_protect",
                    "armor",
                }:
                    return ActionResult(
                        False,
                        "⚠️ O‘zingizni nishon qilib bo‘lmaydi.",
                    )

        action = game.add_night_action(
            actor_id=actor_id,
            action_type=action_type,
            target_id=target_id,
            priority=priority,
            created_at=time.time(),
            data=data,
        )

        self.update_activity(
            chat_id,
            actor_id,
        )

        return ActionResult(
            True,
            "🌙 Harakatingiz qabul qilindi.",
            {"action": action},
        )

    def get_night_actions(
        self,
        chat_id: int,
    ) -> list[NightAction]:
        game = self.get_game(chat_id)

        if game is None:
            return []

        return list(game.night_actions)

    def resolve_night(
        self,
        chat_id: int,
    ) -> ActionResult:
        game = self.get_game(chat_id)

        if game is None:
            return ActionResult(
                False,
                "⚠️ O‘yin topilmadi.",
            )

        if game.phase != GamePhase.NIGHT:
            return ActionResult(
                False,
                "⚠️ Hozir tun bosqichi emas.",
            )

        actions = sorted(
            game.night_actions,
            key=lambda action: action.priority,
        )

        blocked: set[int] = set()
        protected: set[int] = set()
        healed: set[int] = set()
        attacks: list[NightAction] = []
        economic_actions: list[NightAction] = []
        investigation_actions: list[NightAction] = []
        special_actions: list[NightAction] = []

        # --------------------------------------------------------
        # 1. BLOKLASH
        # --------------------------------------------------------

        for action in actions:
            if action.action_type == "block":
                if action.target_id is not None:
                    blocked.add(action.target_id)

        # --------------------------------------------------------
        # 2. HIMOYA
        # --------------------------------------------------------

        for action in actions:
            if action.actor_id in blocked:
                continue

            if action.action_type in {
                "protect",
                "guard",
                "heal",
                "armor",
            }:
                if action.target_id is not None:
                    protected.add(action.target_id)

                if action.action_type == "heal":
                    if action.target_id is not None:
                        healed.add(action.target_id)

        # --------------------------------------------------------
        # 3. KUZATUV / TEKSHIRUV
        # --------------------------------------------------------

        for action in actions:
            if action.actor_id in blocked:
                continue

            if action.action_type in {
                "inspect_team",
                "inspect_role",
                "watch",
                "observe",
                "servant_check",
                "spy",
                "chronicle",
            }:
                investigation_actions.append(action)

        # --------------------------------------------------------
        # 4. IQTISOD
        # --------------------------------------------------------

        for action in actions:
            if action.actor_id in blocked:
                continue

            if action.action_type in {
                "steal_gold",
                "protect_gold",
                "trade",
                "economy",
                "cook",
            }:
                economic_actions.append(action)

        # --------------------------------------------------------
        # 5. HUJUM
        # -
