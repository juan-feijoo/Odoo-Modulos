# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class FinalGenerator(models.Model):
    _inherit = 'final.generator'

    year = fields.Selection(
        selection_add=[],
        default=lambda self: str(fields.Date.today().year)
    )

    @api.depends('year')
    def _compute_date(self):
        for record in self:
            if record.year:
                year_int = int(record.year)
                company = record.company_id
                if company.fiscalyear_last_day and company.fiscalyear_last_month:
                    last_day = company.fiscalyear_last_day
                    last_month = int(company.fiscalyear_last_month)
                    try:
                        record.date = fields.Date.from_string(f'{year_int}-{last_month:02d}-{last_day:02d}')
                    except ValueError:
                        record.date = fields.Date.from_string(f'{year_int}-12-31')
                else:
                    record.date = fields.Date.from_string(f'{year_int}-12-31')
            else:
                record.date = False

    
    #FILTRADO DE CUENTAS Y DIARIOS
    def action_create_move(self):
        self.ensure_one()
        self.line_ids.unlink()

        accounts = self.env['account.account'].search([
            ('deprecated', '=', False),
            ('is_unofficial_account', '=', False)
        ])

        line_vals = []
        for account in accounts:
            balance_data = self.get_yearly_balance(account)
            balance = balance_data['balance']
            if balance:
                first_digit = account.code[0]
                line_type = 'patrimonial' if first_digit in ('1', '2', '3') else 'refundicion' if first_digit in ('4', '5') else False
                
                if line_type:
                    debit = -balance if balance < 0 else 0.0
                    credit = balance if balance > 0 else 0.0
                    
                    line_vals.append((0, 0, {
                        'type': line_type, 'account_id': account.id, 'debit': debit, 'credit': credit,
                        'balance': balance, 'amount_currency': balance_data['amount_currency'],
                        'currency_id': account.currency_id.id, 'final_id': self.id,
                    }))

        self.write({'line_ids': line_vals})
        return True

    def get_yearly_balance(self, account):
        self.ensure_one()
        date_start = f'{self.year}-01-01'
        date_end = self.date
        company_id = self.company_id.id # Obtenemos el ID de la compañía actual
    
        saldo_inicial_query = """
            SELECT SUM(aml.debit - aml.credit)
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN account_journal aj ON am.journal_id = aj.id
            WHERE aml.account_id = %s 
              AND aml.company_id = %s
              AND aml.date < %s 
              AND am.state = 'posted'
              AND (aj.is_unofficial_journal IS NULL OR aj.is_unofficial_journal = FALSE)
        """
        self.env.cr.execute(saldo_inicial_query, (account.id, company_id, date_start))
        saldo_inicial_result = self.env.cr.fetchone()
        saldo_inicial = saldo_inicial_result[0] if saldo_inicial_result and saldo_inicial_result[0] else 0.0
    
        movimiento_periodo_query = """
            SELECT SUM(aml.debit - aml.credit)
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN account_journal aj ON am.journal_id = aj.id
            WHERE aml.account_id = %s 
              AND aml.company_id = %s
              AND aml.date >= %s 
              AND aml.date <= %s 
              AND am.state = 'posted'
              AND (aj.is_unofficial_journal IS NULL OR aj.is_unofficial_journal = FALSE)
        """
        self.env.cr.execute(movimiento_periodo_query, (account.id, company_id, date_start, date_end))
        movimiento_periodo_result = self.env.cr.fetchone()
        movimiento_periodo = movimiento_periodo_result[0] if movimiento_periodo_result and movimiento_periodo_result[0] else 0.0
    
    
        balance = saldo_inicial + movimiento_periodo
        
        currency_query = """
            SELECT SUM(aml.amount_currency), aml.currency_id
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN account_journal aj ON am.journal_id = aj.id
            WHERE aml.account_id = %s 
              AND aml.company_id = %s
              AND aml.date >= %s 
              AND aml.date <= %s 
              AND am.state = 'posted'
              AND (aj.is_unofficial_journal IS NULL OR aj.is_unofficial_journal = FALSE)
            GROUP BY aml.currency_id
            LIMIT 1
        """
        self.env.cr.execute(currency_query, (account.id, company_id, date_start, date_end))
        currency_result = self.env.cr.fetchone()
        
        return {
            'balance': balance,
            'amount_currency': currency_result[0] if currency_result else 0.0,
            'currency_id': currency_result[1] if currency_result else False
    }