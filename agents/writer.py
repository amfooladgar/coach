# agents/writer.py

def format_daily_brief(user, tasks) -> str:
    """Create a Markdown daily brief with reflection tasks labeled."""

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

    return md
