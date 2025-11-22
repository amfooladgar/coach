# app.py
import sqlite3
import datetime
import yaml
import os
from dotenv import load_dotenv

from agents.planner import plan_tasks
from agents.scheduler import schedule_tasks
from agents.writer import format_daily_brief
from agents.reflector import reflect_on_day
from tools.telegram import send_message
from tools.storage import init_db, save_tasks, save_calendar_events

CONFIG_PATH = "config.yaml"

# Load environment variables from .env if available
load_dotenv(dotenv_path=".env")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def save_journal_entry(entry: dict, db_path="data/store.sqlite"):
    """Save reflection into SQLite (one or multiple per day, with mood & gratitude)."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS journal
           (id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            summary TEXT,
            insights TEXT,
            actions TEXT,
            mood TEXT,
            gratitude TEXT,
            created_at TEXT)"""
    )
    def normalize(val):
        # Convert LangChain messages or other objects into plain text
        if hasattr(val, "content"):
            return val.content
        return str(val) if val is not None else ""
    cur.execute(
        "INSERT INTO journal (date, summary, insights, actions, mood, gratitude, created_at) VALUES (?,?,?,?,?,?,?)",
        (
            datetime.date.today().isoformat(),
            normalize(entry.get("summary")),
            normalize(entry.get("insights")),
            normalize(entry.get("actions")),
            normalize(entry.get("mood")),
            normalize(entry.get("gratitude")),
            datetime.datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def run_morning(config):
    """Morning cycle: fetch goals + yesterday’s actions → plan tasks → save + brief"""
    # Init DB
    init_db(config["storage"]["database"])

    # Goals → Planner (with yesterday’s actions) → Tasks
    goals = [g["description"] for g in config["weekly_goals"]]

    max_tasks = config.get("agents", {}).get("planner", {}).get("max_tasks_per_day", 5)
    tasks = plan_tasks(goals, db_path=config["storage"]["database"])
    tasks = tasks[:max_tasks]

    # Save to DB
    save_tasks(tasks, config["storage"]["database"])

    # Schedule tasks to calendar blocks
    schedule = schedule_tasks(tasks, config)
    save_calendar_events(schedule, config["storage"]["database"])

    # Daily brief with schedule
    brief = format_daily_brief(config["user"], tasks, schedule)

    # Send
    if config.get("delivery", {}).get("telegram", False):  ### CHANGED: toggle delivery
        send_message(brief)
    else:
        print("📭 Delivery disabled, printing brief:\n", brief)

    print("🌅 Morning Brief sent")
    print(brief)

def run_evening(config):
    print("📝 Evening reflection time. Enter your thoughts (finish with ENTER twice):")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    journal_text = "\n".join(lines)

    if not journal_text.strip():
        print("⚠️ No reflection entered, skipping.")
        return

    # Reflector agent → structured JSON (summary, insights, actions)
    reflection = reflect_on_day(journal_text, config=config)

    # Save to DB
    save_journal_entry(reflection, config["storage"]["database"])

    # Send formatted message
    msg = (
        f"# 🌙 Evening Reflection\n\n"
        f"**Summary**:\n{reflection['summary']}\n\n"
        f"**Insights**:\n- " + reflection['insights'].replace("\n", "\n- ") + "\n\n"
        f"**Actions for Tomorrow**:\n- " + reflection['actions'].replace("\n", "\n- ")
    )
    # NEW: Add mood & gratitude if present
    if reflection.get("mood"):
        msg += f"\n\n**Mood Rating (1-10):** {reflection['mood']}"
    if reflection.get("gratitude"):
        msg += f"\n\n**Gratitude:** {reflection['gratitude']}"

    ### CHANGED: toggle delivery
    if config.get("delivery", {}).get("telegram", False):
        send_message(msg)
    else:
        print("📭 Delivery disabled, printing reflection:\n", msg)

    print("🌙 Reflection saved & sent")
    print(msg)


if __name__ == "__main__":
    config = load_config()
    ### CHANGED: respect safety config (token limit)
    max_tokens = config.get("safety", {}).get("max_tokens_per_run", None)
    if max_tokens:
        os.environ["COACH_MAX_TOKENS"] = str(max_tokens)
    mode = os.getenv("COACH_MODE", "morning")  # default morning
    if mode == "morning":
        run_morning(config)
    elif mode == "evening":
        run_evening(config)
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)