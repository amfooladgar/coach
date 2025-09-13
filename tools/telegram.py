# tools/telegram.py
import os
import asyncio
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MAX_LEN = 4096  # Telegram hard limit


def send_message(text: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️ Missing Telegram config, printing instead:\n", text)
        return

    async def _send():
        bot = Bot(token=TELEGRAM_TOKEN)
        # Split into chunks if longer than Telegram’s max
        for i in range(0, len(text), MAX_LEN):
            chunk = text[i:i + MAX_LEN]
            await bot.send_message(chat_id=CHAT_ID, text=chunk, parse_mode="Markdown")

    asyncio.run(_send())


def debug_list_chats():
    """
    Helper: prints recent chat IDs from bot updates.
    Run manually to discover correct TELEGRAM_CHAT_ID.
    """
    if not TELEGRAM_TOKEN:
        print("⚠️ Missing TELEGRAM_TOKEN")
        return

    async def _debug():
        bot = Bot(token=TELEGRAM_TOKEN)
        updates = await bot.get_updates()
        if not updates:
            print("ℹ️ No updates found. Send a message to your bot first.")
        for u in updates:
            msg = u.message
            if msg:
                print(
                    f"Chat ID: {msg.chat.id} | Type: {msg.chat.type} | Title/Name: {msg.chat.title or msg.chat.first_name}"
                )

    asyncio.run(_debug())
