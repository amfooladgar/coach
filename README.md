# 🤖 Personal AI Coach (Cost-Optimized Pilot)

A lean, agentic AI system that acts as a personal coach for daily productivity, alignment with values, and long-term growth.
Built with **LangGraph**, **GPT-4o-mini**, **SQLite**, and **Chroma**, this pilot runs locally (or on a small server) and costs **<\$20/month** to operate.

The coach helps you stay aligned with your four pillars:

* 🌉 **Connection** – building and maintaining meaningful relationships
* 🔍 **Curiosity** – continuous learning and exploration
* 🕰 **Presence** – mindfulness, focus, and healthy routines
* 💡 **Contribution** – creating value and giving back

---

## 🚀 Features

* **Daily Briefs** – Morning summary of top tasks, goals, and nudges, delivered via Telegram
* **Task Planner Agent** – Converts weekly goals + yesterday’s reflection into concrete daily tasks
* **Evening Reflector Agent** – Captures journaling, summarizes the day, extracts insights, and proposes actions

  * Supports **mood tracking** (1–10)
  * Supports **gratitude prompts** (1 line)
* **SQLite Persistence** – Local DB to track tasks, reflections, and habits
* **Markdown Reports** – Clean, human-readable briefs and reflections you can view in Telegram or locally
* **Cost Optimized** – Uses GPT-4o-mini for routine planning, keeping token costs under \$10/month

---

## 📂 Project Structure

```
coach/
│── app.py              # Orchestrator (morning/evening run)
│── config.yaml         # User config (goals, keys, schedule, agent settings)
│── requirements.txt
│
├── agents/
│   ├── planner.py      # Plans daily tasks from goals + reflections
│   ├── scheduler.py    # (future) Maps tasks to calendar
│   ├── reflector.py    # Evening journaling + insights, mood, gratitude
│   └── writer.py       # Formats daily briefs for Telegram
│
├── data/
│   ├── schemas.py      # Task DSL (Pydantic schema)
│   └── store.sqlite    # SQLite DB (tasks + reflections)
│
├── tools/
│   ├── calendar.py     # (future) Google Calendar integration
│   ├── rag.py          # Chroma wrapper for personal notes/docs
│   ├── telegram.py     # Send messages to Telegram
│   └── storage.py      # SQLite utilities
```

---

## ⚙️ Setup

### 1. Clone & Install

```bash
git clone <your-repo>
cd coach
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file (or export as env vars):

```dotenv
OPENAI_API_KEY=your_openai_key
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

* Create a Telegram bot using [@BotFather](https://t.me/BotFather).
* Get your chat ID by messaging your bot and checking updates via the Telegram API.

### 3. Configure Coach

Edit `config.yaml` to set:

* User info (name, wake time, gym time, timezone)
* Goals (quarterly, weekly, daily habits)
* Agent settings (planner, reflector with mood/gratitude, etc.)
* Delivery options (Telegram on/off, future Slack/Email)

### 4. Run

Morning (planner):

```bash
COACH_MODE=morning python app.py
```

Evening (reflector):

```bash
COACH_MODE=evening python app.py
```

You’ll see output both:

* Printed in the terminal
* Sent to your Telegram account

### 5. Automate (optional)

Schedule runs with cron (Linux/macOS):

```bash
# Morning brief at 07:30
30 7 * * * COACH_MODE=morning /usr/bin/python3 /path/to/coach/app.py

# Evening reflection at 21:00
0 21 * * * COACH_MODE=evening /usr/bin/python3 /path/to/coach/app.py
```

## 🛠 Roadmap

- [x] ✅ Morning Planner → Daily Brief (Telegram delivery)  
- [x] ✅ Reflector Agent → Evening journaling, insights, mood, gratitude, carry-over actions  
- [ ] 🔜 Scheduler Agent → Auto-map tasks to calendar (respecting gym, sleep, work blocks)  
- [ ] 🔜 RAG Integration → Query personal notes/docs in Chroma  
- [ ] 🔜 Weekly/Monthly OKR Tracking → Align tasks with quarterly objectives  
- [ ] 🔜 Dashboard → Web/Notion-based overview of progress and mood trends  
- [ ] 🔜 Analytics → Track habits, average mood, and goal completion rates  


## 💰 Cost Estimate

* **LLM (GPT-4o-mini)**: \~\$5–15/month depending on usage
* **SQLite + Chroma**: \$0
* **Telegram API**: \$0
* **Optional server (Raspberry Pi / EC2 micro)**: \$0–5/month

👉 **Total Pilot: <\$20/month**

---

## 📖 License

MIT License. Free to use, adapt, and extend.
