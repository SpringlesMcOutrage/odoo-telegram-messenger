from odoo import models, fields, api
from odoo.exceptions import UserError


class TelegramChat(models.Model):
    _name = 'telegram.chat'
    _description = 'Telegram Chat'
    _order = 'id desc'
    _rec_name = 'name'

    name = fields.Char(string='Contact Name', required=True)
    chat_id = fields.Char(string='Telegram Chat ID', required=True)
    username = fields.Char(string='Username')
    phone = fields.Char(string='Phone')
    avatar = fields.Binary(string='Avatar')
    unread_count = fields.Integer(string='Unread', default=0)
    message_ids = fields.One2many('telegram.message', 'chat_id', string='Messages')
    active = fields.Boolean(string='Active', default=True)

    def action_open_chat(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f'Chat with {self.name}',
            'res_model': 'telegram.chat',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def mark_as_read(self):
        self.unread_count = 0
        self.message_ids.filtered(lambda m: not m.is_read and m.is_incoming).write({'is_read': True})

    def send_telegram_message(self, text):
        config = self.env['telegram.config'].get_config()
        result = config.send_message(self.chat_id, text)

        if result:
            self.env['telegram.message'].create({
                'chat_id': self.id,
                'message_id': str(result.get('message_id')),
                'content': text,
                'is_incoming': False,
                'is_read': True,
                'sender_name': 'You',
            })
            return True
        else:
            raise UserError('Failed to send message via Telegram API')
