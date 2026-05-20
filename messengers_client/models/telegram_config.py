from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)


class TelegramConfig(models.Model):
    _name = 'telegram.config'
    _description = 'Telegram Bot Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Name', default='Telegram Bot Configuration', required=True)
    bot_token = fields.Char(string='Bot Token', required=True, help='Token from @BotFather')
    webhook_url = fields.Char(string='Webhook URL', help='URL for receiving messages')
    last_update_id = fields.Integer(string='Last Update ID', default=0, help='For long polling')
    active = fields.Boolean(string='Active', default=True)
    bot_username = fields.Char(string='Bot Username', readonly=True)
    bot_name = fields.Char(string='Bot Name', readonly=True)
    polling_enabled = fields.Boolean(string='Long Polling', default=True,
                                     help='Enable automatic message polling via long polling')

    @api.model
    def get_config(self):
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            raise UserError(_('Please configure a Telegram Bot in Settings → Technical → Telegram Config'))
        return config

    def _get_api_url(self, method):
        return f'https://api.telegram.org/bot{self.bot_token}/{method}'

    def test_connection(self):
        try:
            response = requests.get(self._get_api_url('getMe'), timeout=10)
            result = response.json()

            if result.get('ok'):
                bot_info = result.get('result', {})
                self.write({
                    'bot_username': bot_info.get('username'),
                    'bot_name': bot_info.get('first_name'),
                })
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success!'),
                        'message': _('Successfully connected to bot %s!') % bot_info.get('username'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_('Error: %s') % result.get('description'))

        except requests.exceptions.RequestException as e:
            raise UserError(_('Connection error: %s') % str(e))

    def send_message(self, chat_id, text):
        try:
            response = requests.post(
                self._get_api_url('sendMessage'),
                json={'chat_id': chat_id, 'text': text},
                timeout=10
            )
            result = response.json()

            if not result.get('ok'):
                _logger.error('Telegram API error: %s', result.get('description'))
                return False

            return result.get('result')

        except requests.exceptions.RequestException as e:
            _logger.error('Error sending Telegram message: %s', str(e))
            return False

    def get_updates(self):
        try:
            response = requests.get(
                self._get_api_url('getUpdates'),
                params={
                    'offset': self.last_update_id + 1,
                    'timeout': 30,
                },
                timeout=35
            )
            result = response.json()

            if result.get('ok'):
                updates = result.get('result', [])
                if updates:
                    self.last_update_id = updates[-1]['update_id']
                return updates
            else:
                _logger.error('Telegram API error: %s', result.get('description'))
                return []

        except requests.exceptions.RequestException as e:
            _logger.error('Error getting Telegram updates: %s', str(e))
            return []

    def process_updates(self):
        if not self.polling_enabled:
            return

        updates = self.get_updates()

        for update in updates:
            message = update.get('message')
            if not message:
                continue

            chat = message.get('chat', {})
            from_user = message.get('from', {})
            text = message.get('text', '')

            telegram_chat = self.env['telegram.chat'].search([
                ('chat_id', '=', str(chat.get('id')))
            ], limit=1)

            if not telegram_chat:
                chat_name = from_user.get('first_name', '')
                if from_user.get('last_name'):
                    chat_name += f" {from_user.get('last_name')}"

                telegram_chat = self.env['telegram.chat'].create({
                    'name': chat_name or 'Unknown',
                    'chat_id': str(chat.get('id')),
                    'username': from_user.get('username', ''),
                })

            self.env['telegram.message'].create({
                'chat_id': telegram_chat.id,
                'message_id': str(message.get('message_id')),
                'content': text,
                'is_incoming': True,
                'is_read': False,
                'sender_name': from_user.get('first_name', 'Unknown'),
            })

    @api.model
    def cron_poll_updates(self):
        configs = self.search([('active', '=', True), ('polling_enabled', '=', True)])
        for config in configs:
            try:
                config.process_updates()
            except Exception as e:
                _logger.error('Error polling Telegram updates: %s', str(e))