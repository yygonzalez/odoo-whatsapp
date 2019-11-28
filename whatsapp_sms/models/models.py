# -*- coding: utf-8 -*-
import logging
import json
from odoo.http import request
from odoo import models, fields, api
from odoo.custom_addons.whatsapp_sms.controllers.wabot import WABot
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    send_by_whatsapp = fields.Boolean("Enviar notificaciones por Whatsapp",
                                      config_parameter='whatsapp_sms.whatsapp')


class MailMail(models.Model):

    _inherit = 'mail.mail'
    _inherits = {'mail.message': 'mail_message_id'}

    @api.multi
    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        send_by_whatsapp = self.env['ir.config_parameter'].sudo().get_param('whatsapp_sms.whatsapp')
        for mail_id in self.ids:
            mail = None
            mail = self.browse(mail_id)
            email_list = []
            if mail.email_to:
                email_list.append(mail._send_prepare_values())
            for partner in mail.recipient_ids:
                values = mail._send_prepare_values(partner=partner)
                values['partner_id'] = partner
                values['partner_mobile'] = partner.mobile
                email_list.append(values)
            for email in email_list:
                message = email.get('body_alternative')
                phone = email.get('partner_mobile')
                if send_by_whatsapp:
                    chatID = ""
                    res = {
                        "chatId": chatID,
                        "teléfono": phone,
                        "messages": message
                    }
                    jsons = json.dumps(res)
                    what = WABot(jsons)
                    if phone and message:
                        resp = what.send_message(chatID, phone, message)

        return super(MailMail, self)._send(auto_commit, raise_exception, smtp_session)