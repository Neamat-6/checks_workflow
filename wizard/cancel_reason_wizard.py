# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PaymentCancelReason(models.TransientModel):
    _name = 'payment.cancel.reason'

    cancel_reason = fields.Text('Cancel Reason', required=True)

    def action_confirm(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        for record in self.env['account.payment'].search([('id', 'in', active_ids)]):
            record.cancellation_reason = self.cancel_reason
            record.check_cancel()
