# Strawberry Bot Control Center 🍓

A responsive Django dashboard for managing Telegram bots, message templates, sending messages, and configuring reactions.

## Requirements
- Python 3.10+
- A Telegram bot token from [@BotFather](https://t.me/BotFather) for real bot connections

## Run locally (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py makemigrations control
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

## Telegram notes
- Add a bot in **My bots** with its API token. The app calls Telegram `getMe` to validate the token.
- Messages can be sent only to chats the bot is allowed to access. The recipient field accepts a chat ID or a public channel username (for example `@my_channel`); the bot must be a member/admin as required.
- Telegram Bot API reactions are supported only in eligible chats and with appropriate permissions. The reaction form uses `setMessageReaction` and requires a chat ID plus 

## Included
Dashboard, bot management, message templates, message sending, reaction controls, customization, settings, responsive mobile layout, SQLite, CSRF-protected forms, Django admin.
