import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi. Railway Variables ichiga "
        "BOT_TOKEN qo‘shing."
    )


GAME_NAME = "THRONE"
GAME_TITLE = "Taxtlar O‘yini 👑⚔️"


DEFAULT_GAME_START_TIME = 30
DEFAULT_DAY_TIME = 45
DEFAULT_VOTE_TIME = 45
DEFAULT_NIGHT_TIME = 60


MIN_PLAYERS = 4
MAX_PLAYERS = 36


DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "throne.db",
)


CREATOR_ID = int(
    os.getenv("CREATOR_ID", "0")
)


WEBAPP_URL = os.getenv(
    "WEBAPP_URL",
    "",
).strip()
