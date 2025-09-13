# agents/planner.py

import json
import uuid
import datetime
import os
import sqlite3
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from data.schemas import Task

# Load environment variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(ENV_PATH)

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)


def _clean_json_output(text: str) -> str:
    """Remove markdown fences or language tags from LLM output."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[len("json"):].strip()
    return text


def _normalize_values(t: dict) -> dict:
    """Ensure values match schema patterns, apply safe defaults."""
    allowed_priority = {"P1", "P2", "P3"}
    allowed_energy = {"deep", "steady", "light"}
    allowed_pillar = {"Connection", "Curiosity", "Presence", "Contribution"}
    allowed_status = {"todo", "doing", "done", "blocked"}

    return {
        "task_id": t.get("task_id") or str(uuid.uuid4()),
        "title": t.get("title") or t.get("task") or "Untitled task",
        "why": t.get("why") or "No reason provided",
        "steps": t.get("steps") or [],
        "priority": t.get("priority") if t.get("priority") in allowed_priority else "P3",
        "energy": t.get("energy") if t.get("energy") in allowed_energy else "steady",
        "duration_est_min": t.get("duration_est_min") or 30,
        "due": t.get("due") or datetime.datetime.now().isoformat(),
        "pillar": t.get("pillar") if t.get("pillar") in allowed_pillar else "Contribution",
        "deps": t.get("deps") or [],
        "status": t.get("status") if t.get("status") in allowed_status else "todo",
        "artifact_link": t.get("artifact_link"),
        "source": t.get("source", "goal"),
    }


def _get_yesterdays_actions(db_path="data/store.sqlite") -> list[str]:
    """Fetch actionable lessons from yesterday's reflection (if any)."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS journal (date TEXT PRIMARY KEY, summary TEXT, insights TEXT, actions TEXT, created_at TEXT)"
    )
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    cur.execute(
        "SELECT actions FROM journal WHERE date = ? ORDER BY created_at DESC LIMIT 1",
        (yesterday,),
    )

    row = cur.fetchone()
    conn.close()
    if row and row[0]:
        return [row[0]]
    return []


def plan_tasks(goals: list, db_path="data/store.sqlite") -> list[Task]:
    """Generate tasks from goals + yesterday’s actions using the LLM and map into Task schema."""

    yest_actions = _get_yesterdays_actions(db_path)

    prompt = f"""
    You are the Planner. Convert these weekly goals and yesterday's actions into <=5 tasks for today.

    Weekly Goals:
    {goals}

    Yesterday’s Actions (from reflections):
    {yest_actions}

    Each task must strictly follow this JSON schema:

    {{
      "task_id": "string (UUID)",
      "title": "short descriptive title",
      "why": "reason this task matters (1 sentence)",
      "steps": ["step 1", "step 2", "step 3"],
      "priority": "P1|P2|P3",
      "energy": "deep|steady|light",
      "duration_est_min": "integer (minutes)",
      "due": "ISO 8601 datetime",
      "pillar": "Connection|Curiosity|Presence|Contribution",
      "deps": [],
      "status": "todo|doing|done|blocked",
      "artifact_link": null
    }}

    Rules:
    - Tasks that directly come from Yesterday’s Actions must include `"source": "reflection"`.
    - Tasks that come from Weekly Goals must include `"source": "goal"`.
    - Return ONLY a valid JSON list of Task objects.
    """

    result = llm.invoke(prompt)
    result_text = getattr(result, "content", str(result))
    result_text = _clean_json_output(result_text)

    try:
        raw_tasks = json.loads(result_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}\nOutput was:\n{result_text}")

    tasks: list[Task] = []
    for t in raw_tasks:
        mapped = _normalize_values(t)
        tasks.append(Task(**mapped))

    return tasks
