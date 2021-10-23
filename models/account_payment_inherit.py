# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _



class AccountPayment(models.Model):
    _inherit = "account.payment"

    state = fields.Selection(selection_add=[
        ('checks', 'Check Received'),
        ('under_collected', 'Under Collection/Payment')], ondelete={'checks': 'set default', 'under_collected': 'set default'})
    payment_ref = fields.Char(string='Payment Ref', copy=False)
    first_user_id = fields.Many2one('res.users', string='Users')
    first_move_line = fields.Many2one('account.move.line')
    cancellation_date = fields.Date()
    under_collected_canceled = fields.Boolean(default=False)
    first_move_id = fields.Many2one('account.move')
    second_move_id = fields.Many2one('account.move')
    third_move_id = fields.Many2one('account.move')
    check_no = fields.Char(string='Check No.', copy=False)
    check_printing_payment_method_selected = fields.Boolean(related='journal_id.check_printing_payment_method_selected')
    due_date = fields.Date(string='Due Date')
    effective_date = fields.Date(string='Effective Date', copy=False)
    under_collection_date = fields.Date(string='Under Collection Date', copy=False)
    cancellation_reason = fields.Text(string="Cancellation Reason")
    show_under_collect_button = fields.Boolean(string='Show Under Collect', compute='get_under_collect_button')
    show_validate_check_button = fields.Boolean(string='Show Collect', compute='get_validate_check_button')

    _sql_constraints = [('payment_ref_uniq', 'unique (payment_ref)', 'The Name of Payment Ref must be unique !'), ]

    # @api.depends('state', 'partner_type', 'journal_id')
    # def get_under_collect_button(self):
    #     for payment in self:
    #         if payment.partner_type == 'customer' and payment.state == 'checks':
    #             payment.show_under_collect_button = True
    #
    #         elif payment.partner_type == 'supplier' and payment.state == 'checks' and payment.journal_id.no_of_steps_in_vendor_checks == 'three_steps':
    #             payment.show_under_collect_button = True
    #
    #         elif payment.partner_type == 'supplier' and payment.state == 'checks' and payment.journal_id.no_of_steps_in_vendor_checks == 'two_steps':
    #             payment.show_under_collect_button = False
    #         else:
    #             payment.show_under_collect_button = False
    #
    # @api.depends('state', 'partner_type', 'journal_id')
    # def get_validate_check_button(self):
    #     for payment in self:
    #         if payment.partner_type == 'customer' and payment.state == 'under_collected':
    #             payment.show_validate_check_button = True
    #
    #         elif payment.partner_type == 'supplier' and payment.state == 'under_collected' and payment.journal_id.no_of_steps_in_vendor_checks == 'three_steps':
    #             payment.show_validate_check_button = True
    #
    #         elif payment.partner_type == 'supplier' and payment.state == 'checks' and payment.journal_id.no_of_steps_in_vendor_checks == 'two_steps':
    #             payment.show_validate_check_button = True
    #         else:
    #             payment.show_validate_check_button = False
    #
    # @api.onchange('journal_id')
    # def _get_journal_id(self):
    #     for rec in self:
    #         for payment in rec.journal_id.outbound_payment_method_ids:
    #             if payment.name == 'Check' and rec.payment_type == 'transfer':
    #                 raise ValidationError(
    #                     _("You can't make internal transfer from check."))
    #
    # @api.onchange('destination_journal_id')
    # def _get_destination_journal_id(self):
    #     for rec in self:
    #         for payment in rec.destination_journal_id.outbound_payment_method_ids:
    #             if payment.name == 'Check' and rec.payment_type == 'transfer':
    #                 raise ValidationError(
    #                     _("You can't make internal transfer from check."))
    #
    # def _get_values_multi_currency(self, amount):
    #     for record in self:
    #         account_move_line_obj = self.env['account.move.line'].with_context(check_move_validity=False)
    #         if record.invoice_ids and all(
    #                 [invoice.currency_id == record.invoice_ids[0].currency_id for invoice in record.invoice_ids]):
    #             # if all the invoices selected share the same currency, record the payment in that currency too
    #             invoice_currency = record.invoice_ids[0].currency_id
    #         credit, debit, amount_currency, currency_id = account_move_line_obj.with_context(
    #             date=record.payment_date).compute_amount_fields(record.amount, record.currency_id,
    #                                                              record.company_id.currency_id)
    #         return credit, debit, amount_currency, currency_id
    #
    # def post(self):
    #     """ Create the journal items for the payment and update the payment's state to 'posted'.
    #         A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
    #         and another in the destination reconciliable account (see _compute_destination_account_id).
    #         If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
    #         If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
    #     """
    #     for rec in self:
    #         if rec.journal_id.type == 'bank' and rec.check_printing_payment_method_selected:
    #
    #             if rec.state != 'draft':
    #                 raise ValidationError(
    #                     _("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)
    #
    #             if any(inv.state != 'open' for inv in rec.invoice_ids):
    #                 raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
    #
    #             # keep the name in case of a payment reset to draft
    #             sequence_code = False
    #             if not rec.name:
    #                 # Use the right sequence to set the name
    #                 if rec.payment_type == 'transfer':
    #                     sequence_code = 'account.payment.transfer'
    #                 else:
    #                     if rec.partner_type == 'customer' and rec.payment_type == 'inbound':
    #                         sequence_code = 'account.payment.customer.invoice'
    #                     elif rec.partner_type == 'customer' and rec.payment_type == 'outbound':
    #                         sequence_code = 'account.payment.customer.refund'
    #                     elif rec.partner_type == 'supplier' and rec.payment_type == 'inbound':
    #                         sequence_code = 'account.payment.supplier.refund'
    #                     elif rec.partner_type == 'supplier' and rec.payment_type == 'outbound':
    #                         sequence_code = 'account.payment.supplier.invoice'
    #                 rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
    #                     sequence_code)
    #                 if not rec.name and rec.payment_type != 'transfer':
    #                     raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
    #
    #             # Create the journal entry
    #             amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
    #             move = rec._create_payment_entry(amount)
    #             rec.first_move_id = move.id
    #             # In case of a transfer, the first journal entry created debited the source liquidity account and credited
    #             # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
    #             if rec.payment_type == 'transfer':
    #                 transfer_credit_aml = move.line_ids.filtered(
    #                     lambda r: r.account_id == rec.company_id.transfer_account_id)
    #                 transfer_debit_aml = rec._create_transfer_entry(amount)
    #                 (transfer_credit_aml + transfer_debit_aml).reconcile()
    #
    #             if rec.partner_type == 'customer':
    #                 due_date = False
    #                 for line in move.line_ids:
    #                     due_date = line.date_maturity
    #
    #                 rec.write({'state': 'checks', 'move_name': move.name, 'due_date': due_date})
    #             if rec.partner_type == 'supplier':
    #                 due_date = False
    #                 for line in move.line_ids:
    #                     due_date = line.date_maturity
    #
    #                 rec.write({'state': 'checks', 'move_name': move.name, 'due_date': due_date})
    #         else:
    #             return super(AccountPayment, self).post()
    #
    # def _create_payment_entry(self, amount):
    #     """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
    #         Return the journal entry.
    #     """
    #     aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
    #     invoice_currency = False
    #     if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
    #         # if all the invoices selected share the same currency, record the paiement in that currency too
    #         invoice_currency = self.invoice_ids[0].currency_id
    #     debit, credit, amount_currency, currency_id = aml_obj.with_context(
    #         date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
    #
    #     move = self.env['account.move'].create(self._get_move_vals())
    #
    #     # Write line corresponding to invoice payment
    #     counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
    #     counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
    #     counterpart_aml_dict.update({'currency_id': currency_id})
    #     counterpart_aml = aml_obj.create(counterpart_aml_dict)
    #
    #     # Reconcile with the invoices
    #     if self.payment_difference_handling == 'reconcile' and self.payment_difference:
    #         writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
    #         amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(
    #             self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
    #         # the writeoff debit and credit must be computed from the invoice residual in company currency
    #         # minus the payment amount in company currency, and not from the payment difference in the payment currency
    #         # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
    #         total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
    #         total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount,
    #                                                                                                      self.company_id.currency_id)
    #         if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
    #             amount_wo = total_payment_company_signed - total_residual_company_signed
    #         else:
    #             amount_wo = total_residual_company_signed - total_payment_company_signed
    #         debit_wo = amount_wo > 0 and amount_wo or 0.0
    #         credit_wo = amount_wo < 0 and -amount_wo or 0.0
    #         writeoff_line['name'] = _('Counterpart')
    #         writeoff_line['account_id'] = self.writeoff_account_id.id
    #         writeoff_line['debit'] = debit_wo
    #         writeoff_line['credit'] = credit_wo
    #         writeoff_line['payment_id'] = self.id
    #         writeoff_line['amount_currency'] = amount_currency_wo
    #         writeoff_line['currency_id'] = currency_id
    #         aml_obj.create(writeoff_line)
    #         if counterpart_aml['debit']:
    #             counterpart_aml['debit'] += credit_wo - debit_wo
    #         if counterpart_aml['credit']:
    #             counterpart_aml['credit'] += debit_wo - credit_wo
    #         counterpart_aml['amount_currency'] -= amount_currency_wo
    #
    #     # Write counterpart lines
    #     if not self.currency_id != self.company_id.currency_id:
    #         amount_currency = 0
    #     liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
    #     liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
    #
    #     # checks entry accounts
    #     if self.partner_type == 'customer' and self.check_printing_payment_method_selected:
    #         if not self.journal_id.note_id:
    #             raise ValidationError(_("Notes accounts not found!"))
    #         account = self.journal_id.note_id.id
    #         liquidity_aml_dict.update({'account_id': account, })
    #     elif self.partner_type == 'supplier' and self.check_printing_payment_method_selected:
    #         if not self.journal_id.note_payable_id:
    #             raise ValidationError(_("Notes Payable account not found!"))
    #         account = self.journal_id.note_payable_id.id
    #         liquidity_aml_dict.update({'account_id': account, })
    #     aml_obj.create(liquidity_aml_dict)
    #
    #     if self.journal_id.auto_post_entries:
    #         move.post()
    #         self.invoice_ids.register_payment(counterpart_aml)
    #     return move
    #
    # def under_collected(self):
    #     for record in self:
    #         credit, debit, amount_currency, currency_id = self._get_values_multi_currency(record.amount)
    #         amount_currency = -1 * amount_currency if credit else amount_currency
    #         account_move_obj = self.env['account.move']
    #         journal_vals = {}
    #         line_vals = {}
    #         line_vals2 = {}
    #         line_vals['name'] = "/"
    #         line_vals['partner_id'] = record.partner_id.id
    #         line_vals['payment_id'] = record.id
    #         line_vals['credit'] = credit
    #         line_vals['payment_id'] = record.id
    #         line_vals['debit'] = 0.0
    #         line_vals['amount_currency'] = amount_currency
    #         line_vals['currency_id'] = record.currency_id.id
    #
    #         line_vals2['name'] = "/"
    #         line_vals2['partner_id'] = record.partner_id.id
    #         line_vals2['payment_id'] = record.id
    #         line_vals2['credit'] = 0.0
    #         line_vals2['debit'] = credit
    #         line_vals2['payment_id'] = record.id
    #         line_vals2['amount_currency'] = -1 * amount_currency
    #         line_vals2['currency_id'] = record.currency_id.id
    #
    #         if record.partner_type == 'customer':
    #             if not record.journal_id.under_collected_id:
    #                 raise ValidationError(_("Checks under collection account not found!"))
    #             if not record.journal_id.note_id:
    #                 raise ValidationError(_("Notes account not found!"))
    #             line_vals2[
    #                 'account_id'] = record.journal_id.under_collected_id and record.journal_id.under_collected_id.id or False
    #             line_vals['account_id'] = record.journal_id.note_id and record.journal_id.note_id.id or False
    #
    #         elif record.partner_type == 'supplier':
    #             if not record.journal_id.note_payable_id:
    #                 raise ValidationError(_("Notes Payable account not found!"))
    #             if not record.journal_id.under_payment_id:
    #                 raise ValidationError(_("Checks Under Payment account not found!"))
    #             line_vals2[
    #                 'account_id'] = record.journal_id.note_payable_id and record.journal_id.note_payable_id.id or False
    #             line_vals[
    #                 'account_id'] = record.journal_id.under_payment_id and record.journal_id.under_payment_id.id or False
    #
    #         journal_vals.update({
    #             'journal_id': record.journal_id.id,
    #             'partner_id': record.partner_id.id,
    #             'line_ids': [(0, 0, line_vals), (0, 0, line_vals2)]
    #         })
    #         move = account_move_obj.create(journal_vals)
    #         record.second_move_id = move.id
    #         due_date = False
    #
    #         if move.journal_id.auto_post_entries:
    #             move.post()
    #
    #         for line in move.line_ids:
    #             due_date = line.date_maturity
    #         record.write({'state': 'under_collected',
    #                       'move_name': move.name, 'due_date': due_date, 'under_collected_canceled': True})
    #
    # def validate_check(self):
    #     for record in self:
    #         credit, debit, amount_currency, currency_id = self._get_values_multi_currency(record.amount)
    #         amount_currency = -1 * amount_currency if credit else amount_currency
    #
    #         account_move_obj = self.env['account.move']
    #         journal_vals = {}
    #         line_vals = {}
    #         line_vals2 = {}
    #         if not record.journal_id.under_collected_id:
    #             raise ValidationError(_("Checks under collection account not found!"))
    #         line_vals['name'] = "/"
    #         line_vals['partner_id'] = record.partner_id.id
    #         line_vals['payment_id'] = record.id
    #         line_vals['credit'] = credit
    #         line_vals['debit'] = 0.0
    #         line_vals['date'] = record.under_collection_date or fields.Date.today()
    #         line_vals['amount_currency'] = amount_currency
    #         line_vals['account_id'] = record.journal_id.under_collected_id.id
    #         line_vals['currency_id'] = record.currency_id.id
    #
    #         line_vals2['name'] = "/"
    #         line_vals2['partner_id'] = record.partner_id.id
    #         line_vals2['payment_id'] = record.id
    #         line_vals2['credit'] = 0.0
    #         line_vals2['debit'] = credit
    #         line_vals2['date'] = record.under_collection_date or fields.Date.today()
    #         line_vals2['amount_currency'] = -1 * amount_currency
    #         line_vals2['currency_id'] = record.currency_id.id
    #
    #         if record.partner_type == 'customer':
    #             if not record.journal_id.under_collected_id:
    #                 raise ValidationError(_("Checks under collection account not found!"))
    #             line_vals2[
    #                 'account_id'] = record.journal_id.default_debit_account_id and record.journal_id.default_debit_account_id.id or False
    #             line_vals[
    #                 'account_id'] = record.journal_id.under_collected_id and record.journal_id.under_collected_id.id or False
    #
    #         elif record.partner_type == 'supplier':
    #             if not record.journal_id.under_payment_id and record.journal_id.no_of_steps_in_vendor_checks == 'three_steps':
    #                 raise ValidationError(_("Checks under payment account not found!"))
    #
    #             elif not record.journal_id.note_payable_id and record.journal_id.no_of_steps_in_vendor_checks == 'two_steps':
    #                 raise ValidationError(_("Checks notes payable account not found!"))
    #
    #             if record.journal_id.no_of_steps_in_vendor_checks == 'three_steps':
    #                 line_vals2[
    #                     'account_id'] = record.journal_id.under_payment_id and record.journal_id.under_payment_id.id or False
    #
    #             elif record.journal_id.no_of_steps_in_vendor_checks == 'two_steps':
    #                 line_vals2[
    #                     'account_id'] = record.journal_id.note_payable_id and record.journal_id.note_payable_id.id or False
    #
    #             line_vals[
    #                 'account_id'] = record.journal_id.default_credit_account_id and record.journal_id.default_credit_account_id.id or False
    #
    #         journal_vals.update({
    #             'journal_id': record.journal_id.id,
    #             'partner_id': record.partner_id.id,
    #             'line_ids': [(0, 0, line_vals), (0, 0, line_vals2)]
    #         })
    #         move = account_move_obj.create(journal_vals)
    #
    #         if move.journal_id.auto_post_entries:
    #             move.post()
    #
    #         record.third_move_id = move.id
    #         record.write({'state': 'posted', 'move_name': move.name})
    #
    # def check_cancel(self):
    #     for rec in self:
    #         reverted_move = False
    #         if not rec.cancellation_reason:
    #             raise ValidationError(_("You must add cancellation reason"))
    #         move_arr = []
    #         move_lines = self.env['account.move.line'].search([('payment_id', '=', rec.id)])
    #         for each_move in move_lines:
    #             if each_move.move_id not in move_arr:
    #                 move_arr.append(each_move.move_id)
    #                 rec.due_date = each_move.date_maturity
    #         for move in move_arr:
    #             reverted_move_id = self.env['account.move'].browse(move.id).reverse_moves(move.date,
    #                                                                                       move.journal_id or False)
    #             reverted_move = self.env['account.move'].browse(reverted_move_id)
    #             for line in reverted_move.line_ids:
    #                 line.payment_id = rec.id
    #
    #         rec.state = 'cancelled'
    #         rec.cancellation_date = fields.Date.today()
    #
    # @api.model
    # def create(self, vals):
    #     if vals['payment_type'] == 'transfer':
    #         if self.env['account.journal'].browse(vals['journal_id']).outbound_payment_method_ids:
    #             for each_rec in self.env['account.journal'].browse(vals['journal_id']).outbound_payment_method_ids:
    #                 if each_rec.name == 'Check':
    #                     raise ValidationError(
    #                         _("You can't make internal transfer from check."))
    #         if self.env['account.journal'].browse(vals['destination_journal_id']).outbound_payment_method_ids:
    #             for each_rec in self.env['account.journal'].browse(
    #                     vals['destination_journal_id']).outbound_payment_method_ids:
    #                 if each_rec.name == 'Check':
    #                     raise ValidationError(
    #                         _("You can't make internal transfer from check."))
    #         # Can't make internal transfer from ant to the same account
    #         if vals['destination_journal_id'] == vals['journal_id']:
    #             raise ValidationError(
    #                 _("You can't make internal tranfser from and to the same journal."))
    #     return super(AccountPayment, self).create(vals)
    #
    # def write(self, vals):
    #     for rec in self:
    #         payment = vals['payment_type'] if 'payment_type' in vals else rec.payment_type
    #         if payment == 'transfer':
    #             if 'journal_id' in vals:
    #                 if self.env['account.journal'].browse(vals['journal_id']).outbound_payment_method_ids:
    #                     for each_rec in self.env['account.journal'].browse(
    #                             vals['journal_id']).outbound_payment_method_ids:
    #                         if each_rec.name == 'Check':
    #                             raise ValidationError(
    #                                 _("You can't make internal transfer from check."))
    #             if 'destination_journal_id' in vals:
    #                 if self.env['account.journal'].browse(vals['destination_journal_id']).outbound_payment_method_ids:
    #                     for each_rec in self.env['account.journal'].browse(
    #                             vals['destination_journal_id']).outbound_payment_method_ids:
    #                         if each_rec.name == 'Check':
    #                             raise ValidationError(
    #                                 _("You can't make internal transfer from check."))
    #             # Can't make internal transfer from ant to the same account
    #             de_journal_id = vals[
    #                 'destination_journal_id'] if 'destination_journal_id' in vals else rec.destination_journal_id.id
    #             fr_journal_id = vals['journal_id'] if 'journal_id' in vals else rec.journal_id.id
    #             if de_journal_id == fr_journal_id:
    #                 raise ValidationError(
    #                     _("You can't make internal transfer from and to the same journal."))
    #     return super(AccountPayment, self).write(vals)
    #
    # def roll_back(self):
    #     for record in self:
    #         reverted_payment_move = False
    #         if record.state == 'checks' and not self._context.get('skip_entry'):
    #             record.write({'state': 'draft'})
    #             reverted_payment_move = self.env['account.move'].browse(
    #                 record.first_move_id.reverse_moves(date=record.first_move_id.date))
    #
    #         if record.state == 'under_collected' and not self._context.get('skip_entry'):
    #             record.write({'state': 'checks'})
    #             reverted_payment_move = self.env['account.move'].browse(
    #                 record.second_move_id.reverse_moves(date=record.second_move_id.date))
    #
    #         if record.state == 'posted' and not self._context.get('skip_entry'):
    #             # this is context for module for isky_grant_vendor_payment
    #             if record.partner_type == 'customer':
    #                 record.write({'state': 'under_collected'})
    #
    #             elif record.partner_type == 'supplier' and record.journal_id.no_of_steps_in_vendor_checks == 'three_steps':
    #                 record.write({'state': 'under_collected'})
    #
    #             elif record.partner_type == 'supplier' and record.journal_id.no_of_steps_in_vendor_checks == 'two_steps':
    #                 record.write({'state': 'checks'})
    #
    #             reverted_payment_move = self.env['account.move'].browse(
    #                 record.third_move_id.reverse_moves(date=record.second_move_id.date))
    #
    #         if reverted_payment_move:
    #             for line in reverted_payment_move.line_ids:
    #                 line.payment_id = record.id
    #
    # def check_under_collection_action(self):
    #     for rec in self:
    #         if rec.state == 'checks' and rec.check_printing_payment_method_selected == True:
    #             rec.under_collected()
    #         else:
    #             raise ValidationError(
    #                 _(
    #                     'Only Check Received payment can be Under Collected. Trying to confirm a payment in state draft.'))
    #
    # def validate_check_action(self):
    #     for rec in self:
    #         if rec.state == 'under_collected' and rec.check_printing_payment_method_selected == True:
    #             rec.validate_check()
    #         else:
    #             raise ValidationError(_(
    #                 'Only Under Collected payment can be Validated. Trying to under collect a payment in check received.'))
    #
    # def check_rollback_action(self):
    #     for rec in self:
    #         if rec.state != 'draft' and rec.check_printing_payment_method_selected == True:
    #             rec.roll_back()
    #         else:
    #             raise ValidationError(_('You can not make Check Rollback in Draft state .'))
    #
    # def check_cancel_action(self):
    #     for rec in self:
    #         if rec.state != 'draft' and rec.check_printing_payment_method_selected == True:
    #             rec.check_cancel()
    #         else:
    #             raise ValidationError(_('You can not make Check Cancel in Draft state .'))
