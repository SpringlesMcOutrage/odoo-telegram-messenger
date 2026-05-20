from odoo import models, fields, api


class TelegramMessage(models.Model):
    _name = 'telegram.message'
    _description = 'Telegram Message'
    _order = 'date asc'
    _rec_name = 'content'

    chat_id = fields.Many2one('telegram.chat', string='Chat', required=True, ondelete='cascade')
    message_id = fields.Char(string='Telegram Message ID')
    content = fields.Text(string='Content', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, required=True)
    is_incoming = fields.Boolean(string='Incoming', default=False)
    is_read = fields.Boolean(string='Read', default=False)
    sender_name = fields.Char(string='Sender')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    @api.model
    def create(self, vals):
        message = super().create(vals)
        if message.is_incoming and not message.is_read:
            message.chat_id.unread_count += 1
        return message

    def write(self, vals):
        res = super().write(vals)
        if 'is_read' in vals:
            for message in self:
                if message.is_incoming:
                    if vals['is_read']:
                        message.chat_id.unread_count = max(0, message.chat_id.unread_count - 1)
                    else:
                        message.chat_id.unread_count += 1
        return res