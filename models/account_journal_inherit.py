# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    under_collected_id = fields.Many2one('account.account', string="Checks Under Collection")
    under_payment_id = fields.Many2one('account.account', string="Checks Under Payment")
    note_id = fields.Many2one('account.account', string="Notes Receivable")
    note_payable_id = fields.Many2one('account.account', string="Notes Payable")
    auto_post_entries = fields.Boolean('Auto Post Entries', default=True)
    no_of_steps_in_vendor_checks = fields.Selection([('two_steps', '2 Steps'), ('three_steps', '3 Steps')],
                                                    default='two_steps',
                                                    string='No. Of Steps In Vendor Checks')
