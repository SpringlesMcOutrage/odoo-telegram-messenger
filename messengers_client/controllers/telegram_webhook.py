from odoo import http
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)


class TelegramWebhook(http.Controller):

    @http.route('/telegram/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def telegram_webhook(self, **kwargs):
        try:
            data = request.httprequest.get_json()
            _logger.info('Telegram webhook received: %s', json.dumps(data))

            self._process_update(data)

            return {'ok': True}

        except Exception as e:
            _logger.error('Error processing Telegram webhook: %s', str(e))
            return {'ok': False, 'error': str(e)}

    def _process_update(self, update):
        message = update.get('message')
        if not message:
            return

        chat = message.get('chat', {})
        from_user = message.get('from', {})
        text = message.get('text', '')

        telegram_chat = request.env['telegram.chat'].sudo().search([
            ('chat_id', '=', str(chat.get('id')))
        ], limit=1)

        if not telegram_chat:
            chat_name = from_user.get('first_name', '')
            if from_user.get('last_name'):
                chat_name += f" {from_user.get('last_name')}"

            telegram_chat = request.env['telegram.chat'].sudo().create({
                'name': chat_name or 'Unknown',
                'chat_id': str(chat.get('id')),
                'username': from_user.get('username', ''),
            })

        request.env['telegram.message'].sudo().create({
            'chat_id': telegram_chat.id,
            'message_id': str(message.get('message_id')),
            'content': text,
            'is_incoming': True,
            'is_read': False,
            'sender_name': from_user.get('first_name', 'Unknown'),
        })