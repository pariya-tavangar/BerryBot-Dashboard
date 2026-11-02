# Architecture Overview

## Project layout

```text
BerryBot-Dashboard/
├── berryapp/                  # Main Django app
│   ├── models.py              # TelegramBot, TelegramChat, templates, activity, preferences
│   ├── views.py               # Dashboard, bot management, message sending, reactions, customization
│   ├── utils.py               # Telegram profile image fetcher
│   ├── templates/             # Shared layout and page-specific templates
│   └── migrations/            # Database schema history
├── strawberry/                # Django project configuration
│   ├── settings.py            # Environment and security configuration
│   ├── urls.py               # URL dispatching
│   └── wsgi.py               # WSGI app entry point
├── static/                    # CSS, JS, and image assets
├── media/                     # Uploaded bot profile images
├── db.sqlite3                 # Local development database (contains bot tokens)
├── requirements.txt           # Python runtime dependencies
├── manage.py                  # Django management entry point
└── .env.example               # Local configuration template
```

## App responsibilities

### `berryapp`

- Manages Telegram bot connections and validation
- Saves reusable message templates
- Sends messages to Telegram chats
- Applies emoji reactions to existing Telegram messages
- Stores dashboard preference settings
- Maintains a small activity history for the dashboard summary

### `strawberry`

- Configures Django installed apps, middleware, and static/media directories
- Defines project URL routing
- Loads environment configuration from `.env`

## Key models

### `TelegramBot`

Tracks a single Telegram bot with:

- `name`
- `username`
- `token`
- `profile_image`
- `is_active`
- `created_at`
- `last_checked`

### `MessageTemplate`

Stores reusable message text for the dashboard workflow.

### `Activity`

Logs actions such as bot connections, sent messages, and reactions.

### `UserPreference`

Stores UI preferences such as theme, display name, compact mode, and animations.
Preferences are currently a single global record, not scoped to an account.

### `TelegramChat`

Captures Telegram chats used in bot messaging flows and enforces a unique combination of bot + chat.

## Request flow

1. User visits a page in the dashboard.
2. Django resolves the route from `strawberry/urls.py`.
3. A matching view in `berryapp/views.py` loads the required model data. The
   dashboard fetches only the four bots it displays; selector and management
   pages load the bot list they need.
4. The view returns a rendered template with the relevant context.
5. Template inheritance and page blocks render the final UI.
6. For Telegram interactions, the view sends an HTTP request to Telegram's Bot API and updates the database when appropriate.

## Dependency overview

- Django 5.2
- Pillow for image handling
- Python-dotenv for `.env` support
- Requests for Telegram API calls

## Architectural observations

This project is intentionally compact and appropriate for a personal dashboard.
Its main constraints are operational maturity: access control, token protection,
and isolation of slow external calls.

The dashboard derives bot counts with a single aggregate query. Pages that
already load all bots derive counts from that in-memory list instead of
performing another count query. There is no cache or pagination layer.

All dashboard routes are currently public and bot tokens are stored in
plaintext. The settings page and local-use documentation warn against public
deployment, but these controls are not substitutes for authentication or
authorization.
