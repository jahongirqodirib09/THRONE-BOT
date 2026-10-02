from __future__ import annotations

import aiosqlite

from config import DATABASE_PATH


async def init_db() -> None:
    """THRONE bazasini yaratadi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT NOT NULL,
                language TEXT DEFAULT 'uz',
                gold INTEGER DEFAULT 0,
                coin INTEGER DEFAULT 0,
                diamond INTEGER DEFAULT 0,
                elite_pass INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS game_players (
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role_id TEXT,
                team TEXT,
                alive INTEGER DEFAULT 1,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (chat_id, user_id)
            )
            """
        )

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS game_settings (
                chat_id INTEGER PRIMARY KEY,
                start_time INTEGER DEFAULT 30,
                day_time INTEGER DEFAULT 45,
                vote_time INTEGER DEFAULT 45,
                night_time INTEGER DEFAULT 60
            )
            """
        )

        await db.commit()


async def add_or_update_player(
    user_id: int,
    username: str | None,
    first_name: str,
) -> None:
    """O‘yinchini bazaga qo‘shadi yoki yangilaydi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO players (
                user_id,
                username,
                first_name
            )
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
            """,
            (
                user_id,
                username,
                first_name,
            ),
        )

        await db.commit()


async def get_player(
    user_id: int,
) -> dict | None:
    """Bitta o‘yinchi ma’lumotini oladi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM players
            WHERE user_id = ?
            """,
            (user_id,),
        )

        row = await cursor.fetchone()

        if row is None:
            return None

        return dict(row)


async def add_group(
    chat_id: int,
    title: str | None,
) -> None:
    """Guruhni bazaga qo‘shadi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO groups (
                chat_id,
                title
            )
            VALUES (?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                title = excluded.title
            """,
            (
                chat_id,
                title,
            ),
        )

        await db.commit()


async def get_group(
    chat_id: int,
) -> dict | None:
    """Guruh ma’lumotini oladi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM groups
            WHERE chat_id = ?
            """,
            (chat_id,),
        )

        row = await cursor.fetchone()

        if row is None:
            return None

        return dict(row)


async def add_game_player(
    chat_id: int,
    user_id: int,
    role_id: str | None = None,
    team: str | None = None,
) -> None:
    """O‘yinchini joriy o‘yinga qo‘shadi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO game_players (
                chat_id,
                user_id,
                role_id,
                team,
                alive
            )
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET
                role_id = excluded.role_id,
                team = excluded.team,
                alive = 1
            """,
            (
                chat_id,
                user_id,
                role_id,
                team,
            ),
        )

        await db.commit()


async def remove_game_player(
    chat_id: int,
    user_id: int,
) -> None:
    """O‘yinchini joriy o‘yindan chiqaradi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            DELETE FROM game_players
            WHERE chat_id = ?
            AND user_id = ?
            """,
            (
                chat_id,
                user_id,
            ),
        )

        await db.commit()


async def get_game_players(
    chat_id: int,
) -> list[dict]:
    """Guruhdagi o‘yinchilarni qaytaradi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM game_players
            WHERE chat_id = ?
            ORDER BY joined_at ASC
            """,
            (chat_id,),
        )

        rows = await cursor.fetchall()

        return [dict(row) for row in rows]


async def get_alive_players(
    chat_id: int,
) -> list[dict]:
    """Faqat tirik o‘yinchilarni qaytaradi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM game_players
            WHERE chat_id = ?
            AND alive = 1
            ORDER BY joined_at ASC
            """,
            (chat_id,),
        )

        rows = await cursor.fetchall()

        return [dict(row) for row in rows]


async def get_game_player(
    chat_id: int,
    user_id: int,
) -> dict | None:
    """Bitta o‘yinchining joriy o‘yindagi ma’lumotini oladi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM game_players
            WHERE chat_id = ?
            AND user_id = ?
            """,
            (
                chat_id,
                user_id,
            ),
        )

        row = await cursor.fetchone()

        if row is None:
            return None

        return dict(row)


async def set_player_role(
    chat_id: int,
    user_id: int,
    role_id: str,
    team: str,
) -> None:
    """O‘yinchiga rol va jamoa beradi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            UPDATE game_players
            SET role_id = ?,
                team = ?
            WHERE chat_id = ?
            AND user_id = ?
            """,
            (
                role_id,
                team,
                chat_id,
                user_id,
            ),
        )

        await db.commit()


async def kill_player(
    chat_id: int,
    user_id: int,
) -> None:
    """O‘yinchini o‘lik holatga o‘tkazadi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            UPDATE game_players
            SET alive = 0
            WHERE chat_id = ?
            AND user_id = ?
            """,
            (
                chat_id,
                user_id,
            ),
        )

        await db.commit()


async def get_game_settings(
    chat_id: int,
) -> dict:
    """Guruh o‘yin sozlamalarini qaytaradi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM game_settings
            WHERE chat_id = ?
            """,
            (chat_id,),
        )

        row = await cursor.fetchone()

        if row is not None:
            return dict(row)

        await db.execute(
            """
            INSERT INTO game_settings (
                chat_id,
                start_time,
                day_time,
                vote_time,
                night_time
            )
            VALUES (?, 30, 45, 45, 60)
            """,
            (chat_id,),
        )

        await db.commit()

        return {
            "chat_id": chat_id,
            "start_time": 30,
            "day_time": 45,
            "vote_time": 45,
            "night_time": 60,
        }


async def update_game_settings(
    chat_id: int,
    start_time: int | None = None,
    day_time: int | None = None,
    vote_time: int | None = None,
    night_time: int | None = None,
) -> None:
    """Guruh o‘yin sozlamalarini yangilaydi."""

    settings = await get_game_settings(chat_id)

    new_start_time = (
        start_time
        if start_time is not None
        else settings["start_time"]
    )

    new_day_time = (
        day_time
        if day_time is not None
        else settings["day_time"]
    )

    new_vote_time = (
        vote_time
        if vote_time is not None
        else settings["vote_time"]
    )

    new_night_time = (
        night_time
        if night_time is not None
        else settings["night_time"]
    )

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            UPDATE game_settings
            SET start_time = ?,
                day_time = ?,
                vote_time = ?,
                night_time = ?
            WHERE chat_id = ?
            """,
            (
                new_start_time,
                new_day_time,
                new_vote_time,
                new_night_time,
                chat_id,
            ),
        )

        await db.commit()


async def reset_game_players(
    chat_id: int,
) -> None:
    """Guruhdagi joriy o‘yinchilarni tozalaydi."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            DELETE FROM game_players
            WHERE chat_id = ?
            """,
            (chat_id,),
        )

        await db.commit()
