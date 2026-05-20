# -*- coding: utf-8 -*-
{
    'name': 'Telegram Messenger Integration',
    'version': '18.0.1.0.0',
    'category': 'Discuss',
    'author': 'deep',
    'website': 'https://github.com/SpringlesMcOutrage',
    'summary': 'Receive and send Telegram messages directly inside Odoo',
    'description': """
Telegram Messenger Integration
===============================
Connect your Odoo instance to a Telegram bot and manage conversations
without leaving the Odoo backend.

Features
--------
* Telegram bot configuration — connect any bot via BotFather token
* Long polling — receive messages automatically without a public server
* Webhook support — alternative to polling for production environments
* Chat list — browse all active Telegram chats in one view
* Message history — read and send messages per chat
* Mini messenger UI — a dedicated sidebar panel for quick replies
* Scheduled polling — configurable cron interval (default: every minute)

Setup
-----
1. Create a Telegram bot via @BotFather and copy the token
2. Go to Discuss → Telegram → Configuration
3. Paste the token and choose polling or webhook mode
4. Start the bot — chats appear automatically as users write in

Requirements
------------
* Odoo 18.0
* Python ``requests`` library (included in Odoo standard environment)
* A running Odoo instance reachable from the internet (webhook mode only)
    """,
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/messengers_menu.xml',
        'views/telegram_config_views.xml',
        'views/telegram_chat_views.xml',
        'views/telegram_message_views.xml',
        'data/telegram_cron.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'messengers_client/static/src/css/telegram_messenger.css',
            'messengers_client/static/src/js/telegram_messenger.js',
            'messengers_client/static/src/xml/telegram_messenger.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}