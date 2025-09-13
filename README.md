# 🤖 Personal AI Coach (Cost-Optimized Pilot)

A lean, agentic AI system that acts as a **personal coach** for daily productivity, alignment with values, and long-term growth.
Built with **LangGraph, GPT-4o-mini, SQLite, and Chroma**, this pilot runs locally (or on a small server) and costs **<\$20/month** to operate.

The coach helps you stay aligned with your **four pillars**:

* 🌉 **Connection** – building and maintaining meaningful relationships
* 🔍 **Curiosity** – continuous learning and exploration
* 🕰 **Presence** – mindfulness, focus, and healthy routines
* 💡 **Contribution** – creating value and giving back

---

## 🚀 Features

* **Daily Briefs**: Morning summary of top tasks, goals, and nudges, delivered via Telegram
* **Task Planner Agent**: Converts weekly goals into concrete daily tasks (with priority, energy, and purpose)
* **SQLite Persistence**: Local database to track tasks and goals
* **Markdown Reports**: Clean, human-readable briefs you can view in Telegram or locally
* **Cost Optimized**: Uses GPT-4o-mini for routine planning, keeping token costs under **\$10/month**

---

## 📂 Project Structure

```
coach/
│── app.py              # Orchestrator (morning run)
│── config.yaml          # User config (goals, keys, schedule times)
│── requirements.txt
│
├── agents/
│   ├── planner.py       # Plans daily tasks from goals
│   ├── scheduler.py     # (future) Maps tasks to calendar
│   ├── reflector.py     # (future) Evening journaling + insights
│   └── writer.py        # (future) Formats daily briefs, posts, messages
│
├── data/
│   ├── schemas.py       # Task DSL (Pydantic schema)
│   └── store.sqlite     # SQLite DB (local persistence)
│
├── tools/
│   ├── calendar.py      # (future) Google Calendar integration
│   ├── rag.py           # Chroma wrapper for personal notes/docs
│   ├── telegram.py      # Send messages to Telegram
│   └── storage.py       # SQLite utilities
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

Export required environment variables:

```bash
export OPENAI_API_KEY="your_openai_key"
export TELEGRAM_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

* Create a Telegram bot using [@BotFather](https://t.me/botfather).
* Get your chat ID by messaging your bot and checking updates via Telegram API.

### 3. Run

```bash
python app.py
```

You should see a daily brief both:

* Printed in the terminal
* Sent to your Telegram account

### 4. Automate (optional)

Add a cron job for daily runs at 7:30 AM:

```bash
30 7 * * * /usr/bin/python3 /path/to/coach/app.py
```

---

## 🛠 Roadmap

* [x] ✅ Morning Planner → Daily Brief (Telegram delivery)
* [ ] 🔜 Reflector Agent → Evening journaling & insights
* [ ] 🔜 Scheduler Agent → Auto-map tasks to calendar (respecting gym, sleep, etc.)
* [ ] 🔜 RAG Integration → Query personal notes/docs in Chroma
* [ ] 🔜 Weekly/Monthly OKR tracking → Align tasks with goals
* [ ] 🔜 Dashboard → Web or Notion-based overview of progress

---

## 💰 Cost Estimate

* **LLM (GPT-4o-mini)**: \~\$5–15/month depending on usage
* **SQLite + Chroma**: \$0
* **Telegram API**: \$0
* **Optional server (Raspberry Pi / EC2 micro)**: \$0–5/month

👉 Total Pilot: **<\$20/month**

---

## 📖 License

MIT License. Free to use, adapt, and extend.
