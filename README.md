# Miss Rose V1 Pro Bot

A modular Telegram group-management bot (group admin tools, warns, notes,
filters, welcomes, locks, anti-flood, blacklists, RSS, and more), upgraded
and hardened for production deployment.

- **Bot:** [@MissRoseV1Pro_Bot](https://t.me/MissRoseV1Pro_Bot)
- **Updates channel:** [@BotBaseOfficial](https://t.me/BotBaseOfficial)

This is an updated fork of the classic Marie/Rose-family `tg_bot` codebase,
migrated onto a modern, maintained `python-telegram-bot` release, with
deployment fixes for Render + UptimeRobot, a 64-bit Telegram user-ID
database fix, and a compatibility shim for APIs that were removed upstream.

## What was fixed in this upgrade

- **Dependency pins updated** to `python-telegram-bot==13.15` (last release
  with the synchronous `Updater`/`Dispatcher` API this codebase uses) and
  matching `SQLAlchemy`, `psycopg2-binary`, `feedparser`, `Flask`, etc.
  The old `requirements.txt` had no version pins at all and pulled in a
  `python-telegram-bot` release incompatible with this code.
- **`RegexHandler` compatibility shim** (`tg_bot/modules/helper_funcs/regex_compat.py`)
  — `telegram.ext.RegexHandler` was removed from the library years ago;
  several modules (`afk`, `sed`, `notes`, `reporting`, `disable`) still
  depend on it. It's re-implemented and patched back in before any module
  loads.
- **64-bit Telegram user IDs**: `user_id` columns that were `Integer`
  (32-bit) are now `BigInteger`, so the bot no longer breaks on newer,
  larger Telegram account IDs (a known, previously-unfixed bug in this
  codebase family).
- **Keep-alive web server** (`keep_alive.py`): a tiny Flask app that binds
  `$PORT` and answers `/`, `/health`, `/ping`. Render (or any host that
  expects a "web" process) needs something bound to `$PORT` to consider the
  deploy healthy — and UptimeRobot needs a URL to ping to keep the free-tier
  instance from sleeping.
- **Stale webhook cleanup**: the bot now calls `delete_webhook()` before
  starting long polling, so it can't end up in the "online in Telegram, but
  silently receiving nothing" state.
- Removed a hardcoded, unrelated sudo user ID that had been left in
  `tg_bot/__init__.py`.
- Config loading simplified: setting a `TOKEN` environment variable is now
  enough to switch the bot into "environment config" mode — you don't have
  to separately set `ENV=True` as well.
- `runtime.txt`, `Procfile`, `render.yaml`, and `.env.example` added/updated
  for one-click Render deployment.

## Environment variables

Copy `.env.example` and fill it in. At minimum you need:

| Variable | Required | Description |
|---|---|---|
| `TOKEN` | ✅ | Bot token from [@BotFather](https://t.me/BotFather) |
| `OWNER_ID` | ✅ | Your numeric Telegram user ID |
| `DATABASE_URL` | recommended | Postgres connection string (SQLite is used only if this is unset, and is **not** recommended for a real deployment — it won't survive redeploys on Render) |
| `OWNER_USERNAME` | optional | Your Telegram @username |
| `BOT_USERNAME` | optional | Defaults to `MissRoseV1Pro_Bot` |
| `UPDATE_CHANNEL` | optional | Defaults to `BotBaseOfficial` |
| `SUDO_USERS` / `SUPPORT_USERS` / `WHITELIST_USERS` | optional | Space-separated numeric user IDs |
| `WEBHOOK` | optional | Leave `False` (default) — long polling + `keep_alive.py` is what this repo is tuned for |

## Deploying on Render

1. Push this project to a GitHub repo.
2. In Render, click **New → Blueprint** and point it at the repo (it will
   pick up `render.yaml` automatically), or create a **New Web Service**
   manually with:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python3 -m tg_bot`
3. Add a free **Postgres** database in Render (or any Postgres provider),
   and set `DATABASE_URL` to its connection string.
4. Set `TOKEN` and `OWNER_ID` (and any optional vars) in the Render
   dashboard's Environment tab.
5. Deploy. Once live, open `https://<your-service>.onrender.com/health` —
   you should see a small JSON status response.
6. In **UptimeRobot**, create an HTTP(s) monitor pointing at
   `https://<your-service>.onrender.com/health`, checked every 5 minutes.
   This keeps the free-tier instance awake and gives you an UP/DOWN history.

## Deploying on a VPS

```bash
git clone <your-repo-url> miss-rose-bot
cd miss-rose-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env with your TOKEN, OWNER_ID, DATABASE_URL, etc.
export $(grep -v '^#' .env | xargs)   # or use a process manager that loads .env for you

python3 -m tg_bot
```

For a persistent VPS deployment, run it under a process manager, e.g.:

```bash
# systemd example
sudo tee /etc/systemd/system/missrose-bot.service <<'EOF'
[Unit]
Description=Miss Rose V1 Pro Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/miss-rose-bot
EnvironmentFile=/path/to/miss-rose-bot/.env
ExecStart=/path/to/miss-rose-bot/venv/bin/python3 -m tg_bot
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now missrose-bot
```

## Local development without Postgres

If `DATABASE_URL` is unset, `tg_bot/config.py` falls back to a local SQLite
file (`miss_rose.db`) — fine for testing, not recommended in production
since Render's filesystem is ephemeral.

## Module toggling

- `LOAD` — space-separated list of module names to load exclusively.
- `NO_LOAD` — space-separated list of module names to skip (defaults to
  `translation`, which needs extra setup and API keys not covered here).

## Credits

Originally based on the open-source Marie/Rose-family `tg_bot` project by
PaulSonOfLars and contributors, upgraded here for a modern, production
Render deployment.
