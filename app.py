# app.py
import sqlite3
import datetime
import yaml
import os
from dotenv import load_dotenv

from agents.planner import plan_tasks
from agents.writer import format_daily_brief
from tools.telegram import send_message
from tools.storage import init_db, save_tasks

CONFIG_PATH = "config.yaml"

# Load environment variables from .env if available
load_dotenv(dotenv_path=".env")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()

    # Init DB
    init_db(config["storage"]["database"])

    # Goals → Planner → Tasks
    goals = [g["description"] for g in config["goals"]]
    tasks = plan_tasks(goals)

    # Save to DB
    save_tasks(tasks, config["storage"]["database"])

    # Daily brief
    brief = format_daily_brief(config["user"], tasks)

    # Send to Telegram (falls back to print if no keys)
    send_message(brief)

    print(brief)
