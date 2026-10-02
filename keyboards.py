from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ============================================================
# LOBBY
# ============================================================

def lobby_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⚔️ O‘yinga qo‘shilish",
                    callback_data="lobby_join",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🚪 O‘yindan chiqish",
                    callback_data="lobby_leave",
                ),
            ],
            [
                InlineKeyboardButton(
                    "👥 O‘yinchilar",
                    callback_data="lobby_players",
                ),
                InlineKeyboardButton(
                    "📜 Qoidalar",
                    callback_data="lobby_rules",
                ),
            ],
            [
                InlineKeyboardButton(
                    "👑 O‘yinni boshlash",
                    callback_data="game_start",
                ),
            ],
        ]
    )


# ============================================================
# LOBBY PLAYER LIST
# ============================================================

def lobby_players_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "↩️ Orqaga",
                    callback_data="lobby_back",
                ),
            ],
        ]
    )


# ============================================================
# GAME MAIN MENU
# ============================================================

def game_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "👤 Kabinet",
                    callback_data="menu_profile",
                ),
                InlineKeyboardButton(
                    "🎭 Mening rolim",
                    callback_data="menu_role",
                ),
            ],
            [
                InlineKeyboardButton(
                    "👥 O‘yinchilar",
                    callback_data="menu_players",
                ),
                InlineKeyboardButton(
                    "📜 Qoidalar",
                    callback_data="menu_rules",
                ),
            ],
        ]
    )


# ============================================================
# PRIVATE ROLE MENU
# ============================================================

def role_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎯 Harakatni tanlash",
                    callback_data="role_action_menu",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🤝 Sheriklarim",
                    callback_data="role_teammates",
                ),
            ],
            [
                InlineKeyboardButton(
                    "↩️ Orqaga",
                    callback_data="game_menu",
                ),
            ],
        ]
    )


# ============================================================
# NIGHT ACTION MENU
# ============================================================

def night_action_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎯 Nishon tanlash",
                    callback_data="night_target_menu",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🛡️ Himoya",
                    callback_data="night_protect_menu",
                ),
                InlineKeyboardButton(
                    "⚔️ Hujum",
                    callback_data="night_attack_menu",
                ),
            ],
            [
                InlineKeyboardButton(
                    "👁️ Kuzatuv",
                    callback_data="night_info_menu",
                ),
            ],
            [
                InlineKeyboardButton(
                    "💰 Iqtisod",
                    callback_data="night_economy_menu",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🍳 Oshpaz",
                    callback_data="night_cook_menu",
                ),
            ],
        ]
    )


# ============================================================
# TARGET LIST
# ============================================================

def target_keyboard(
    players: list[tuple[int, str]],
    prefix: str = "target",
    include_none: bool = False,
) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    for user_id, name in players:
        buttons.append(
            [
                InlineKeyboardButton(
                    name,
                    callback_data=f"{prefix}:{user_id}",
                )
            ]
        )

    if include_none:
        buttons.append(
            [
                InlineKeyboardButton(
                    "⏭️ Hech kim",
                    callback_data=f"{prefix}:none",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "↩️ Orqaga",
                callback_data="night_action_menu",
            ),
        ]
    )

    return InlineKeyboardMarkup(buttons)


# ============================================================
# PROTECTION
# ============================================================

def protection_keyboard(
    players: list[tuple[int, str]],
) -> InlineKeyboardMarkup:
    return target_keyboard(
        players=players,
        prefix="protect",
    )


# ============================================================
# ATTACK
# ============================================================

def attack_keyboard(
    players: list[tuple[int, str]],
) -> InlineKeyboardMarkup:
    return target_keyboard(
        players=players,
        prefix="attack",
    )


# ============================================================
# INVESTIGATION
# ============================================================

def investigation_keyboard(
    players: list[tuple[int, str]],
) -> InlineKeyboardMarkup:
    return target_keyboard(
        players=players,
        prefix="inspect",
    )


# ============================================================
# ECONOMY
# ============================================================

def economy_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "💰 Oltin",
                    callback_data="economy_gold",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🪙 Coin",
                    callback_data="economy_coin",
                ),
            ],
            [
                InlineKeyboardButton(
                    "↩️ Orqaga",
                    callback_data="night_action_menu",
                ),
            ],
        ]
    )


# ============================================================
# OSHPAZ
# ============================================================

def cook_keyboard(
    players: list[tuple[int, str]],
) -> InlineKeyboardMarkup:
    return target_keyboard(
        players=players,
        prefix="cook",
    )


# ============================================================
# SPECIAL ACTIONS
# ============================================================

def special_action_keyboard(
    role_key: str | None,
) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    if role_key == "ritsar":
        buttons.append(
            [
                InlineKeyboardButton(
                    "🛡️ Zirhni faollashtirish",
                    callback_data="special_armor",
                ),
            ]
        )

    elif role_key == "shahzoda":
        buttons.append(
            [
                InlineKeyboardButton(
                    "👑 Maxsus himoya",
                    callback_data="special_prince",
                ),
            ]
        )

    elif role_key == "surgun_shahzoda":
        buttons.append(
            [
                InlineKeyboardButton(
                    "🏰 Qaytish",
                    callback_data="special_return",
                ),
            ]
        )

    elif role_key == "taxt_davogari":
        buttons.append(
            [
                InlineKeyboardButton(
                    "👑 Taxtga da’vo",
                    callback_data="special_claim_throne",
                ),
            ]
        )

    elif role_key == "telba":
        buttons.append(
            [
                InlineKeyboardButton(
                    "🃏 Maxsus harakat",
                    callback_data="special_madness",
                ),
            ]
        )

    if not buttons:
        buttons.append(
            [
                InlineKeyboardButton(
                    "↩️ Orqaga",
                    callback_data="role_action_menu",
                ),
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    "↩️ Orqaga",
                    callback_data="role_action_menu",
                ),
            ]
        )

    return InlineKeyboardMarkup(buttons)


# ============================================================
# VOTING
# ============================================================

def voting_keyboard(
    players: list[tuple[int, str]],
) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    for user_id, name in players:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"⚖️ {name}",
                    callback_data=f"vote:{user_id}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "⚪ Hech kim",
                callback_data="vote:none",
            ),
        ]
    )

    return InlineKeyboardMarkup(buttons)


# ============================================================
# PLAYER INFORMATION
# ============================================================

def players_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🟢 Tiriklar",
                    callback_data="players_alive",
                ),
                InlineKeyboardButton(
                    "☠️ Vafot etganlar",
                    callback_data="players_dead",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🚪 Chiqib ketganlar",
                    callback_data="players_left",
                ),
            ],
            [
                InlineKeyboardButton(
                    "↩️ Orqaga",
                    callback_data="game_menu",
                ),
            ],
        ]
    )


# ============================================================
# RULES
# ============================================================

def rules_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "👑 Jamoalar",
                    callback_data="rules_teams",
                ),
                InlineKeyboardButton(
                    "🎭 Rollar",
                    callback_data="rules_roles",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🌙 Tun",
                    callback_data="rules_night",
                ),
                InlineKeyboardButton(
                    "☀️ Kun",
                    callback_data="rules_day",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🗳️ Ovoz berish",
                    callback_data="rules_voting",
                ),
            ],
            [
                InlineKeyboardButton(
                    "↩️ Orqaga",
                    callback_data="game_menu",
                ),
            ],
        ]
    )


# ============================================================
# BACK BUTTON
# ============================================================

def back_keyboard(
    callback_data: str = "game_menu",
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "↩️ Orqaga",
                    callback_data=callback_data,
                ),
            ]
        ]
    )


# ============================================================
# CONFIRMATION
# ============================================================

def confirmation_keyboard(
    yes_callback: str,
    no_callback: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Tasdiqlash",
                    callback_data=yes_callback,
                ),
                InlineKeyboardButton(
                    "❌ Bekor qilish",
                    callback_data=no_callback,
                ),
            ]
        ]
  )
