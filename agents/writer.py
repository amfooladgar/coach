# agents/writer.py
def format_daily_brief(user, tasks) -> str:
    """Create a Markdown daily brief"""
    md = f"# 🌅 Daily Brief for {user['name']}\n\n"
    md += f"🕒 Wake: {user['wake_time']} | 🏋 Gym: {user['gym_time']}\n\n"
    for t in tasks:
        md += f"- **{t.title}** ({t.priority}, {t.pillar})\n  - {t.why}\n"
    return md
