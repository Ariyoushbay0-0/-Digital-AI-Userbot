from telethon import TelegramClient, events
import sqlite3
from datetime import datetime
from openai import OpenAI

# ================= CONFIG =================
client = OpenAI(api_key="your api key")

DB_NAME = "bot.db"

api_id = "your-api-id"
api_hash = "your-api-hash"
session_name = "ai_account_project"

ar = TelegramClient(session_name, api_id, api_hash)

logging_mode = False
MY_ID = None

# ================= SETUP =================
async def setup():
    global MY_ID
    me = await ar.get_me()
    MY_ID = me.id


# ================= DATABASE =================
def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        chat_id INTEGER,
        message TEXT,
        created_at TEXT,
        is_outgoing INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS persona (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# ================= LOGGING =================
@ar.on(events.NewMessage)
async def logger(event):
    global logging_mode

    sender = await event.get_sender()
    if sender and getattr(sender, "bot", False):
        return

    if not logging_mode:
        return

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO chat_logs
        (user_id, chat_id, message, created_at, is_outgoing)
        VALUES (?, ?, ?, ?, ?)
    """, (
        event.sender_id,
        event.chat_id,
        event.raw_text or "[media]",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        int(event.out)
    ))

    conn.commit()
    conn.close()


# ================= COMMANDS =================
@ar.on(events.NewMessage(pattern=r"^/log_on$"))
async def log_on(event):
    global logging_mode
    logging_mode = True
    await event.reply("🟢 Logging ON")


@ar.on(events.NewMessage(pattern=r"^/log_off$"))
async def log_off(event):
    global logging_mode
    logging_mode = False
    await event.reply("🔴 Logging OFF")


@ar.on(events.NewMessage(pattern=r"^/check$"))
async def check(event):
    await event.reply("⚡ Bot is alive")


@ar.on(events.NewMessage(pattern=r"^/help$"))
async def help(event):
    await event.reply("""
📦 Commands:
 /log_on
 /log_off
 /build_persona
 /ai <text>
 /check
""")


@ar.on(events.NewMessage(pattern=r"^/save$"))
async def save(event):
    if not event.is_reply:
        return await event.reply("Reply to a message")

    msg = await event.get_reply_message()

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO chat_logs (user_id, chat_id, message, created_at, is_outgoing) VALUES (?, ?, ?, ?, ?)",
        (msg.sender_id, event.chat_id, msg.raw_text or "[media]", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
    )

    conn.commit()
    conn.close()

    await event.reply("💾 Saved")


# ================= PERSONA BUILDER =================
@ar.on(events.NewMessage(pattern=r"^/build_persona$"))
async def build_persona(event):

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT message
        FROM chat_logs
        WHERE is_outgoing = 1
        ORDER BY id DESC
        LIMIT 300
    """)

    msgs = [r[0] for r in cur.fetchall()]

    if not msgs:
        return await event.reply("No data")

    avg_len = sum(len(m) for m in msgs) / len(msgs)

    prompt = f"""
You are an AI that mimics the user.

Behavior analysis:
- avg message length: {avg_len:.1f}
- style: short, casual, slightly humorous
- response: direct, no fluff

You are the user's digital personality clone.
"""

    cur.execute(
        "INSERT INTO persona (prompt, created_at) VALUES (?, ?)",
        (prompt, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    conn.commit()
    conn.close()

    await event.reply("🧠 Persona created")


# ================= AI CHAT =================
@ar.on(events.NewMessage(pattern=r"^/ai (.+)"))
async def ai(event):

    user_text = event.pattern_match.group(1)

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT prompt FROM persona
        ORDER BY id DESC
        LIMIT 1
    """)
    row = cur.fetchone()

    persona = row[0] if row else "You are a helpful assistant."

    cur.execute("""
        SELECT message
        FROM chat_logs
        ORDER BY id DESC
        LIMIT 15
    """)

    memory = "\n".join(r[0] for r in cur.fetchall())

    conn.close()

    messages = [
        {
            "role": "system",
            "content": persona + "\n\nMemory:\n" + memory
        },
        {
            "role": "user",
            "content": user_text
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        answer = response.choices[0].message.content
        await event.reply(answer)

    except Exception as e:
        await event.reply(f"Error: {e}")


# ================= START =================
init_db()

async def main():
    await ar.start()
    await setup()
    print("🤖 Digital AI Userbot Running...")
    await ar.run_until_disconnected()

ar.loop.run_until_complete(main())

#archive this because i dont have ai api
