# 🤖 Digital AI Userbot

A Telegram AI Userbot that logs conversations, builds a user personality profile, and can generate AI-based responses using OpenAI.

## ✨ Features

* 📩 Telegram userbot using Telethon
* 💾 SQLite message logging
* 🧠 Persona builder based on user writing style
* 🤖 AI chat integration with OpenAI
* 🔍 Message history memory
* ⚡ Simple command system

---

## 📦 Requirements

* Python 3.10+
* Telegram API credentials
* OpenAI API Key (only for AI features)

---

## ⚙️ Configuration

Edit the configuration section:

```python
api_id = YOUR_API_ID
api_hash = "YOUR_API_HASH"

client = OpenAI(
    api_key="YOUR_OPENAI_KEY"
)
```

Get Telegram API credentials from:

https://my.telegram.org

---

## ▶️ Running

Start the userbot:

```bash
python main.py
```

The first run will ask for:

* Telegram phone number
* Login code
* Two-step verification password (if enabled)

---

## 📚 Commands

| Command          | Description                     |
| ---------------- | ------------------------------- |
| `/check`         | Check bot status                |
| `/help`          | Show commands                   |
| `/log_on`        | Enable message logging          |
| `/log_off`       | Disable message logging         |
| `/save`          | Save a replied message          |
| `/build_persona` | Create user personality profile |
| `/ai <text>`     | Ask AI using memory and persona |

---

## 🗄️ Database

The project uses SQLite.

Database file:

```
bot.db
```

Tables:

### chat_logs

Stores:

* User ID
* Chat ID
* Message content
* Timestamp
* Message direction

### persona

Stores:

* Generated personality prompt
* Creation time

---

## 🧠 How Persona Works

The bot analyzes previous outgoing messages:

* Average message length
* Writing style
* Response style

Then it creates a system prompt that represents the user's communication style.

---

## 🔐 Security Notes

Do not upload:

```
api_hash
OpenAI API Key
session files
bot.db
```

to public repositories.

Use environment variables for production deployments.

---

## 🚧 Future Improvements

* [ ] Better personality analysis
* [ ] Long-term memory system
* [ ] Vector database support
* [ ] Local AI model support
* [ ] Web dashboard
* [ ] Message search system
