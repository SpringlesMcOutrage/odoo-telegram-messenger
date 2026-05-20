# Telegram Messenger Integration

> Bring Telegram directly into your Odoo backend — receive messages, reply to customers, and manage conversations without switching apps.

[![Odoo 18](https://img.shields.io/badge/Odoo-18.0-875A7B?style=flat&logo=odoo)](https://odoo.com)
[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Version](https://img.shields.io/badge/Version-18.0.1.0.0-green.svg)](https://github.com/SpringlesMcOutrage/odoo-telegram-messenger)

---

## Overview

**Telegram Messenger Integration** connects your Odoo instance to a Telegram bot, turning Odoo into a full-featured messaging hub. Your support team can read and respond to Telegram messages right inside the Discuss module — no separate app, no tab switching.

Works with both **long polling** (no public URL needed, great for development and private servers) and **webhooks** (production-grade, instant delivery).

---

## Features

### Bot Configuration
- Connect any Telegram bot via its BotFather token — no coding required
- Test connection with one click (validates token, fetches bot name/username)
- Support for multiple bots via separate configuration records

### Message Reception
- **Long polling** — Odoo polls Telegram automatically on a configurable cron schedule (default: every 60 seconds); works behind NAT/firewall, no public URL needed
- **Webhook** — instant message delivery via HTTPS endpoint; ideal for production deployments

### Messenger UI
- **Chat list view** — browse all active Telegram conversations in one screen
- **Message history** — read full conversation threads per chat
- **Inline reply** — send messages back to Telegram without leaving Odoo
- **Unread counter** — see how many unread messages each chat has
- **Mini messenger panel** — a sidebar widget for quick replies from anywhere in the backend

### Automation
- Scheduled cron job polls all active bots at a configurable interval
- New chats are created automatically when a user first writes to the bot
- Incoming messages are stored with sender name, timestamp, and read status

### Translations
Available in: 🇬🇧 English · 🇺🇦 Ukrainian · 🇩🇪 German · 🇪🇸 Spanish

---

## Requirements

| Dependency | Version / Notes |
|-----------|----------------|
| Odoo | 18.0 |
| Python `requests` | included in Odoo standard environment |
| Public HTTPS URL | **webhook mode only** (not needed for long polling) |

---

## Installation

1. Copy the `messengers_client` folder into your Odoo addons directory
2. Restart the Odoo server
3. Go to **Settings → Apps**, click **Update Apps List**
4. Search for **Telegram Messenger Integration** and click **Install**

---

## Setup

### Long Polling (recommended for most setups)

```
1. Open @BotFather in Telegram
2. Send /newbot and follow the prompts
3. Copy the bot token (looks like 123456:ABC-DEF...)
4. In Odoo → Discuss → Telegram → Configuration
5. Paste the token and click "Test Connection"
6. Enable "Long Polling" and save
7. The scheduled cron starts fetching messages automatically
8. Send a message to your bot → it appears in Discuss → Telegram → Chats
```

### Webhook (production)

```
1. Complete steps 1–5 above
2. Enter your public HTTPS URL in the "Webhook URL" field
   (e.g. https://myodoo.example.com/telegram/webhook)
3. Save — Odoo registers the webhook with Telegram automatically
4. Messages are now delivered instantly via HTTP POST
```

---

## Architecture

```
messengers_client/
├── models/
│   ├── telegram_config.py      # Bot config, API calls, polling, webhook registration
│   ├── telegram_chat.py        # Chat records (one per Telegram conversation)
│   └── telegram_message.py     # Individual messages (in/out)
├── controllers/
│   └── telegram_webhook.py     # HTTP endpoint for incoming webhook payloads
├── views/
│   ├── messengers_menu.xml     # Top-level Discuss submenu
│   ├── telegram_config_views.xml
│   ├── telegram_chat_views.xml
│   └── telegram_message_views.xml
├── data/
│   └── telegram_cron.xml       # Scheduled action (cron) for long polling
├── static/src/
│   ├── js/telegram_messenger.js    # Mini messenger sidebar widget (OWL)
│   ├── css/telegram_messenger.css
│   └── xml/telegram_messenger.xml  # OWL template
├── security/
│   └── ir.model.access.csv
└── i18n/
    ├── uk.po
    ├── de.po
    └── es.po
```

---

## Data Model

```
telegram.config
├── bot_token (Char, required)
├── bot_username (Char, readonly — fetched from Telegram)
├── bot_name (Char, readonly)
├── polling_enabled (Boolean)
├── webhook_url (Char, optional)
└── last_update_id (Integer — long polling offset)

telegram.chat
├── chat_id (Char — Telegram's numeric chat ID)
├── name (Char — sender's display name)
├── username (Char)
└── message_ids → telegram.message

telegram.message
├── chat_id → telegram.chat
├── message_id (Char — Telegram message ID)
├── content (Text)
├── sender_name (Char)
├── is_incoming (Boolean)
└── is_read (Boolean)
```

---

## License

[LGPL-3](https://www.gnu.org/licenses/lgpl-3.0) © [deep](https://github.com/SpringlesMcOutrage)
