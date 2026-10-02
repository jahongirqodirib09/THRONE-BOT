from __future__ import annotations

import logging
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import (
    BOT_TOKEN,
    GAME_NAME,
    GAME_TITLE,
    MAX_PLAYERS,
    MIN_PLAYERS,
)
from game_engine import GameEngine
from game_state import GamePhase, PlayerStatus
from keyboards import (
    attack_keyboard,
    back_keyboard,
    cook_keyboard,
    economy_keyboard,
    game_main_keyboard,
    investigation_keyboard,
    lobby_keyboard,
    lobby_players_keyboard,
    night_action_menu_keyboard,
    players_keyboard,
    protection_keyboard,
    role_menu_keyboard,
    rules_keyboard,
    special_action_keyboard,
    target_keyboard,
    voting_keyboard,
)

logger = logging.getLogger(__name__)


# ============================================================
# GLOBAL GAME STORAGE
# ============================================================

ENGINES: dict[int, GameEngine] = {}


def get_engine(chat_id: int) -> GameEngine:
    """Chat uchun GameEngine qaytaradi."""
    if chat_id not in ENGINES:
        ENGINES[chat_id] = GameEngine(chat_id)

    return ENGINES[chat_id]


def get_chat_id(update: Update) -> Optional[int]:
    """Update ichidan chat ID oladi."""
    if update.effective_chat:
        return update.effective_chat.id

    if update.callback_query and update.callback_query.message:
        return update.callback_query.message.chat.id

    return None


def get_user_id(update: Update) -> Optional[int]:
    """Update ichidan user ID oladi."""
    if update.effective_user:
        return update.effective_user.id

    return None


def is_private(update: Update) -> bool:
    return bool(
        update.effective_chat
        and update.effective_chat.type == "private"
    )


async def safe_answer(
    update: Update,
    text: Optional[str] = None,
    show_alert: bool = False,
) -> None:
    """Callback query'ni xavfsiz yopadi."""
    query = update.callback_query

    if not query:
        return

    try:
        await query.answer(
            text=text,
            show_alert=show_alert,
        )
    except Exception:
        pass


async def safe_edit(
    update: Update,
    text: str,
    reply_markup=None,
) -> None:
    """Xabarni xavfsiz tahrirlaydi."""
    query = update.callback_query

    if not query:
        return

    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
        )
    except Exception:
        try:
            if query.message:
                await query.message.reply_text(
                    text,
                    reply_markup=reply_markup,
                )
        except Exception:
            logger.exception("Xabarni tahrirlashda xato.")


async def safe_private_message(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    text: str,
    reply_markup=None,
) -> bool:
    """Userga private xabar yuboradi."""
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=reply_markup,
        )
        return True
    except Exception:
        logger.exception(
            "Private xabar yuborilmadi: %s",
            user_id,
        )
        return False


# ============================================================
# PLAYER HELPERS
# ============================================================

def player_name(player) -> str:
    """Player obyektidan ismni xavfsiz oladi."""
    if player is None:
        return "Noma'lum"

    name = getattr(player, "name", None)

    if name:
        return str(name)

    username = getattr(player, "username", None)

    if username:
        return f"@{username}"

    return str(
        getattr(
            player,
            "user_id",
            "Noma'lum",
        )
    )


def player_role_name(player) -> str:
    role = getattr(player, "role", None)

    if role is None:
        return "Roli aniqlanmagan"

    name = getattr(role, "name", None)

    if name:
        return str(name)

    return str(role)


def player_role_key(player) -> Optional[str]:
    role = getattr(player, "role", None)

    if role is None:
        return None

    key = getattr(role, "key", None)

    if key:
        return str(key)

    role_id = getattr(role, "role_id", None)

    if role_id:
        return str(role_id)

    return None


def get_player(engine: GameEngine, user_id: int):
    """Engine'dagi playerni topishga harakat qiladi."""

    players = getattr(
        engine.state,
        "players",
        {},
    )

    if isinstance(players, dict):
        player = players.get(user_id)

        if player is not None:
            return player

        player = players.get(str(user_id))

        if player is not None:
            return player

    getter = getattr(
        engine,
        "get_player",
        None,
    )

    if callable(getter):
        try:
            return getter(user_id)
        except Exception:
            pass

    return None


def alive_players(engine: GameEngine) -> list:
    players = getattr(
        engine.state,
        "players",
        {},
    )

    if isinstance(players, dict):
        players = list(players.values())

    result = []

    for player in players:
        status = getattr(
            player,
            "status",
            None,
        )

        if status == PlayerStatus.ALIVE:
            result.append(player)

    return result


def all_players(engine: GameEngine) -> list:
    players = getattr(
        engine.state,
        "players",
        {},
    )

    if isinstance(players, dict):
        return list(players.values())

    return list(players)


# ============================================================
# /START
# ============================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Botga /start berilganda ishlaydi."""

    if not update.effective_user:
        return

    user = update.effective_user

    if is_private(update):
        text = (
            f"👑 <b>{GAME_NAME}</b>\n\n"
            f"<b>{GAME_TITLE}</b>\n\n"
            "Strategiya. Qirollik. Sadoqat. Xiyonat.\n\n"
            "🎮 O‘yinni guruhda boshlang.\n"
            "📩 Rolingiz va maxsus topshiriqlaringiz "
            "shaxsiy chat orqali yuboriladi."
        )

        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=game_main_keyboard(),
        )
        return

    chat_id = update.effective_chat.id
    engine = get_engine(chat_id)

    text = (
        f"👑 <b>{GAME_TITLE}</b>\n\n"
        "Qirollik o‘yinini boshlash uchun "
        "quyidagi tugmani bosing.\n\n"
        f"👥 O‘yinchilar: 0/{MAX_PLAYERS}\n"
        f"⚔️ Minimal o‘yinchi: {MIN_PLAYERS}"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=lobby_keyboard(),
    )


# ============================================================
# /NEWGAME
# ============================================================

async def new_game_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Yangi o‘yin lobby'sini ochadi."""

    if not update.effective_chat:
        return

    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "⚔️ Yangi o‘yin guruh chatida ochiladi."
        )
        return

    member = await update.effective_chat.get_member(
        update.effective_user.id
    )

    if member.status not in (
        "administrator",
        "creator",
    ):
        await update.message.reply_text(
            "🔒 Yangi o‘yinni faqat guruh administratori boshlashi mumkin."
        )
        return

    chat_id = update.effective_chat.id

    # Eski engine o‘rniga yangi lobby.
    ENGINES[chat_id] = GameEngine(chat_id)

    engine = ENGINES[chat_id]

    text = (
        f"👑 <b>{GAME_TITLE}</b>\n\n"
        "⚔️ Yangi qirollik o‘yini ochildi.\n\n"
        "O‘yinga qo‘shilish uchun "
        "«👑 O‘yinga qo‘shilish» tugmasini bosing.\n\n"
        f"👥 O‘yinchilar: 0/{MAX_PLAYERS}\n"
        f"🎯 Boshlash uchun kamida {MIN_PLAYERS} kishi kerak."
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=lobby_keyboard(),
    )


# ============================================================
# CALLBACK ROUTER
# ============================================================

async def callback_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Barcha inline tugmalar shu yerga keladi.
    """

    query = update.callback_query

    if not query:
        return

    data = query.data or ""
    chat_id = get_chat_id(update)
    user_id = get_user_id(update)

    if chat_id is None or user_id is None:
        await safe_answer(
            update,
            "Xatolik yuz berdi.",
            True,
        )
        return

    engine = get_engine(chat_id)

    # --------------------------------------------------------
    # LOBBY
    # --------------------------------------------------------

    if data in (
        "join_game",
        "lobby_join",
    ):
        await join_game(
            update,
            context,
            engine,
        )
        return

    if data in (
        "lobby_players",
        "players_lobby",
    ):
        await show_lobby_players(
            update,
            engine,
        )
        return

    if data in (
        "start_game",
        "lobby_start",
    ):
        await start_game(
            update,
            context,
            engine,
        )
        return

    # --------------------------------------------------------
    # MAIN MENU
    # --------------------------------------------------------

    if data in (
        "main_menu",
        "back_main",
        "home",
    ):
        await safe_answer(update)

        await safe_edit(
            update,
            (
                f"👑 <b>{GAME_TITLE}</b>\n\n"
                "Asosiy boshqaruv paneli."
            ),
            game_main_keyboard(),
        )
        return

    # --------------------------------------------------------
    # ROLE
    # --------------------------------------------------------

    if data in (
        "my_role",
        "role",
        "role_info",
    ):
        await show_my_role(
            update,
            context,
            engine,
        )
        return

    # --------------------------------------------------------
    # PLAYERS
    # --------------------------------------------------------

    if data in (
        "players",
        "player_list",
        "alive_players",
    ):
        await show_players(
            update,
            engine,
        )
        return

    # --------------------------------------------------------
    # NIGHT
    # --------------------------------------------------------

    if data in (
        "night_actions",
        "night_menu",
    ):
        await show_night_menu(
            update,
            engine,
        )
        return

    if data in (
        "block",
        "night_block",
    ):
        await show_target_menu(
            update,
            engine,
            "block",
        )
        return

    if data in (
        "protect",
        "night_protect",
    ):
        await show_target_menu(
            update,
            engine,
            "protect",
        )
        return

    if data in (
        "investigate",
        "night_investigate",
    ):
        await show_target_menu(
            update,
            engine,
            "investigate",
        )
        return

    if data in (
        "economy",
        "night_economy",
    ):
        await show_economy_menu(
            update,
            engine,
        )
        return

    if data in (
        "attack",
        "night_attack",
    ):
        await show_target_menu(
            update,
            engine,
            "attack",
        )
        return

    if data in (
        "cook",
        "night_cook",
    ):
        await show_target_menu(
            update,
            engine,
            "cook",
        )
        return

    if data in (
        "special",
        "special_action",
    ):
        await show_special_menu(
            update,
            engine,
        )
        return

    # --------------------------------------------------------
    # TARGET ACTION
    # --------------------------------------------------------

    if data.startswith("target:"):
        await process_target_action(
            update,
            context,
            engine,
            data,
        )
        return

    if data.startswith("action:"):
        await process_action(
            update,
            context,
            engine,
            data,
        )
        return

    # --------------------------------------------------------
    # VOTING
    # --------------------------------------------------------

    if data in (
        "vote",
        "voting",
        "start_voting",
    ):
        await show_voting(
            update,
            engine,
        )
        return

    if data.startswith("vote:"):
        await process_vote(
            update,
            context,
            engine,
            data,
        )
        return

    # --------------------------------------------------------
    # RULES
    # --------------------------------------------------------

    if data in (
        "rules",
        "game_rules",
    ):
        await show_rules(
            update,
        )
        return

    # --------------------------------------------------------
    # ECONOMY
    # --------------------------------------------------------

    if data in (
        "shop",
        "economy_menu",
    ):
        await show_economy_menu(
            update,
            engine,
        )
        return

    # --------------------------------------------------------
    # BACK
    # --------------------------------------------------------

    if data in (
        "back",
        "back_menu",
        "cancel",
    ):
        await safe_answer(update)

        await safe_edit(
            update,
            (
                f"👑 <b>{GAME_TITLE}</b>\n\n"
                "Kerakli bo‘limni tanlang."
            ),
            game_main_keyboard(),
        )
        return

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    await safe_answer(
        update,
        "Bu tugma hozir mavjud emas.",
        True,
    )


# ============================================================
# JOIN GAME
# ============================================================

async def join_game(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    engine: GameEngine,
) -> None:
    query = update.callback_query
    user = update.effective_user

    if not user:
        return

    try:
        result = engine.add_player(
            user_id=user.id,
            name=user.full_name,
            username=user.username,
        )
    except TypeError:
        try:
            result = engine.add_player(
                user.id,
                user.full_name,
            )
        except Exception:
            logger.exception("Player qo‘shishda xato.")
            await safe_answer(
                update,
                "O‘yinga qo‘shishda xatolik.",
                True,
            )
            return
    except Exception:
        logger.exception("Player qo‘shishda xato.")
        await safe_answer(
            update,
            "O‘yinga qo‘shishda xatolik.",
            True,
        )
        return

    success = getattr(
        result,
        "success",
        None,
    )

    message = getattr(
        result,
        "message",
        None,
    )

    if success is False:
        await safe_answer(
            update,
            message or "O‘yinga qo‘shilib bo‘lmadi.",
            True,
        )
        return

    await safe_answer(
        update,
        "👑 Siz o‘yinga qo‘shildingiz!",
    )

    players = all_players(engine)

    text = (
        f"👑 <b>{GAME_TITLE}</b>\n\n"
        "⚔️ O‘yinchilar yig‘ilmoqda.\n\n"
        f"👥 O‘yinchilar: {len(players)}/{MAX_PLAYERS}\n"
        f"🎯 Minimal: {MIN_PLAYERS}\n\n"
        "Ishtirok etish uchun tugmani bosing."
    )

    await safe_edit(
        update,
        text,
        lobby_keyboard(),
    )


# ============================================================
# LOBBY PLAYERS
# ============================================================

async def show_lobby_players(
    update: Update,
    engine: GameEngine,
) -> None:
    await safe_answer(update)

    players = all_players(engine)

    if not players:
        text = (
            "👑 <b>THRONE — O‘yinchilar</b>\n\n"
            "Hozircha hech kim qo‘shilmagan."
        )
    else:
        lines = [
            "👑 <b>THRONE — O‘yinchilar</b>",
            "",
        ]

        for index, player in enumerate(
            players,
            start=1,
        ):
            lines.append(
                f"{index}. {player_name(player)}"
            )

        text = "\n".join(lines)

    await safe_edit(
        update,
        text,
        lobby_players_keyboard(),
    )


# ============================================================
# START GAME
# ============================================================

async def start_game(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    engine: GameEngine,
) -> None:
    query = update.callback_query

    if not query or not query.message:
        return

    user = update.effective_user

    try:
        member = await context.bot.get_chat_member(
            chat_id=query.message.chat.id,
            user_id=user.id,
        )

        if member.status not in (
            "administrator",
            "creator",
        ):
            await safe_answer(
                update,
                "🔒 O‘yinni faqat administrator boshlashi mumkin.",
                True,
            )
            return

    except Exception:
        logger.exception(
            "Admin tekshiruvda xato."
        )
        await safe_answer(
            update,
            "Administrator huquqini tekshirib bo‘lmadi.",
            True,
        )
        return

    players = all_players(engine)

    if len(players) < MIN_PLAYERS:
        await safe_answer(
            update,
            f"Kamida {MIN_PLAYERS} ta o‘yinchi kerak.",
            True,
        )
        return

    try:
        result = engine.start_game()
    except Exception:
        logger.exception(
            "O‘yinni boshlashda xato."
        )
        await safe_answer(
            update,
            "O‘yinni boshlashda texnik xatolik.",
            True,
        )
        return

    success = getattr(
        result,
        "success",
        True,
    )

    if success is False:
        await safe_answer(
            update,
            getattr(
                result,
                "message",
                "O‘yin boshlanmadi.",
            ),
            True,
        )
        return

    await safe_answer(
        update,
        "👑 O‘yin boshlandi!",
    )

    # --------------------------------------------------------
    # PRIVATE ROLE MESSAGES
    # --------------------------------------------------------

    for player in all_players(engine):
        user_id = getattr(
            player,
            "user_id",
            None,
        )

        if not user_id:
            continue

        role = player_role_name(player)

        private_text = (
            f"👑 <b>{GAME_TITLE}</b>\n\n"
            "🎭 <b>Sizning rolingiz:</b>\n"
        
