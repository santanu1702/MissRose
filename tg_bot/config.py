# Local/VPS configuration file.
#
# NOTE: On Render (or Heroku, Docker, etc.) you do NOT need to edit this
# file at all - just set environment variables (see .env.example / README)
# and the bot will automatically use those instead (see tg_bot/__init__.py,
# the `ENV` switch).
#
# This file is only used for local/VPS runs where you prefer editing a
# file over exporting environment variables.

from tg_bot.sample_config import Config as _BaseConfig


class Config(_BaseConfig):
    # REQUIRED - get this from @BotFather
    API_KEY = "YOUR_BOT_TOKEN_HERE"

    # REQUIRED - your numeric Telegram user id (get it from @MissRoseV1Pro_Bot's /id, or @userinfobot)
    OWNER_ID = 0

    OWNER_USERNAME = "YOUR_USERNAME_HERE"

    # RECOMMENDED - postgres connection string, e.g.
    # postgresql://user:password@localhost:5432/miss_rose
    SQLALCHEMY_DATABASE_URI = 'sqlite:///miss_rose.db'

    MESSAGE_DUMP = None
    LOAD = []
    NO_LOAD = ['translation']

    WEBHOOK = False
    URL = None
    PORT = 5000
    CERT_PATH = None

    SUDO_USERS = []
    SUPPORT_USERS = []
    WHITELIST_USERS = []
    DONATION_LINK = None
    DEL_CMDS = False
    STRICT_GBAN = False
    WORKERS = 8
    BAN_STICKER = 'CAADAgADOwADPPEcAXkko5EB3YGYAg'
    ALLOW_EXCL = False

    # Cosmetic
    BOT_USERNAME = "MissRoseV1Pro_Bot"
    UPDATE_CHANNEL = "BotBaseOfficial"


class Production(Config):
    LOGGER = False


class Development(Config):
    LOGGER = True
