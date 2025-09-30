# -*- coding: utf-8 -*-
from odoo import models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def _fill_bank_cash_dashboard_data(self, dashboard_data):

        super()._fill_bank_cash_dashboard_data(dashboard_data)

        journals_to_fix = self.filtered(lambda j: j.type in ('bank', 'cash'))
        if not journals_to_fix:
            return

        account_ids = journals_to_fix.mapped('default_account_id').ids
        if not account_ids:
            return

        balance_data = self.env['account.move.line']._read_group(
            [('account_id', 'in', account_ids), ('parent_state', '=', 'posted')],
            ['account_id'],
            ['balance:sum'],
        )
        balance_map = {account.id: balance for account, balance in balance_data}

       
        for journal in journals_to_fix:
            currency = journal.currency_id or journal.company_id.sudo().currency_id
            true_balance = balance_map.get(journal.default_account_id.id, 0.0)

            dashboard_data[journal.id]['account_balance'] = currency.format(true_balance)