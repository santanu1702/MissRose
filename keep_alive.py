"""
Lightweight Flask web server used to keep the bot's Render (or any other
PaaS) web service alive, and to give UptimeRobot (or any uptime monitor)
something to ping.

The Telegram bot itself talks to Telegram over long-polling in a background
thread; Render only considers a "web" service healthy if it binds $PORT and
answers HTTP requests, so this small server exists purely for that purpose.
"""
import logging
import os
import threading
import time

from flask import Flask, jsonify

LOGGER = logging.getLogger(__name__)

app = Flask(__name__)

START_TIME = time.time()


@app.route("/")
def index():
    return "Miss Rose V1 Pro is alive and running! 🌹"


@app.route("/health")
@app.route("/ping")
@app.route("/status")
def health():
    return jsonify({
        "status": "ok",
        "bot": "@MissRoseV1Pro_Bot",
        "update_channel": "@BotBaseOfficial",
        "uptime_seconds": round(time.time() - START_TIME, 2),
    })


def _run():
    port = int(os.environ.get("PORT", 5000))
    # use_reloader must stay off - it forks a second process otherwise,
    # which would double-start the bot's polling loop.
    app.run(host="0.0.0.0", port=port, use_reloader=False)


def keep_alive():
    """Start the Flask server in a daemon thread and return immediately."""
    thread = threading.Thread(target=_run, name="keep_alive", daemon=True)
    thread.start()
    LOGGER.info("keep_alive: web server thread started on port %s",
                os.environ.get("PORT", 5000))
    return thread
