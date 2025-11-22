# agents/writer.py
from typing import List, Optional
from data.schemas import Task, CalendarEvent


def format_daily_brief(user, tasks: List[Task], schedule: Optional[List[CalendarEvent]] = None) -> str:
    """Create a Markdown daily brief with tasks and schedule."""

    md = f"# 🌅 Daily Brief for {user['name']}\n\n"
    md += f"🕒 Wake: {user['wake_time']} | 🏋 Gym: {user['gym_time']}\n\n"

    # Split tasks
    reflection_tasks = [t for t in tasks if getattr(t, "source", "goal") == "reflection"]
    goal_tasks = [t for t in tasks if getattr(t, "source", "goal") == "goal"]

    if reflection_tasks:
        md += "## 🔁 Reflection Carry-Over\n"
        for t in reflection_tasks:
            md += f"- **{t.title}** ({t.priority}, {t.pillar})\n  - {t.why}\n"

    if goal_tasks:
        md += "\n## 🎯 Weekly Goals\n"
        for t in goal_tasks:
            md += f"- **{t.title}** ({t.priority}, {t.pillar})\n  - {t.why}\n"

    # Add schedule if available
    if schedule:
        md += "\n---\n\n## 📅 Today's Schedule\n\n"
        for event in schedule:
            start_str = event.start_time.strftime("%H:%M")
            end_str = event.end_time.strftime("%H:%M")
            
            # Add emoji/indicator based on block type
            if event.block_type == "fixed":
                icon = "🔒"
            elif event.block_type == "work":
                icon = "💼"
            elif event.block_type == "break":
                icon = "☕"
            else:
                icon = "📌"
            
            md += f"{start_str} - {end_str}  {icon} {event.title}\n"

    return md

