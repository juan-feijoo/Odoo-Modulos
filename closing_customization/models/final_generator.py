# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import datetime

class FinalGenerator(models.Model):
    _inherit = 'final.generator'

    year = fields.Selection(
        selection_add=[],
        default=lambda self: str(fields.Date.today().year)
    )

    date = fields.Date(
        string='Fecha de Cierre',
        compute='_compute_date',
        store=True,
        readonly=True,
        precompute=True
    )

    @api.depends('year', 'company_id')
    def _compute_date(self):
        """
        Calcula la fecha de cierre basándose en la configuración del año fiscal
        de la compañía (res.company).
        """
        for record in self:
            # Si no hay año seleccionado, limpiamos la fecha
            if not record.year:
                record.date = False
                continue

            try:
                year_int = int(record.year)
            except ValueError:
                record.date = False
                continue

            # Determinamos la compañía (la del registro o la del entorno actual)
            company = record.company_id or self.env.company
            
            last_month = int(company.fiscalyear_last_month) if company.fiscalyear_last_month else 12
            last_day = company.fiscalyear_last_day if company.fiscalyear_last_day else 31

            try:
                calculated_date = datetime.date(year_int, last_month, 1) + relativedelta(day=last_day)
                record.date = calculated_date
            except (ValueError, IndexError):
                record.date = datetime.date(year_int, 12, 31)

    def action_create_move(self):
        self.ensure_one()
        if not self.date:
            raise UserError("El año seleccionado no ha generado una fecha de cierre válida. Revise la configuración contable.")
        
        self.line_ids.unlink()
        
        company_id = self.company_id.id
        
        # Buscamos cuentas de la compañía actual que no sean "No Fiscales"
        accounts = self.env['account.account'].search([
            ('company_id', '=', company_id),
            ('deprecated', '=', False),
            ('is_unofficial_account', '=', False)
        ])
        
        line_vals = []
        for account in accounts:
            balance_data = self.get_yearly_balance(account)
            if not self.company_id.currency_id.is_zero(balance_data['balance']):
                balance = balance_data['balance']
                
                first_digit = account.code[0]
                line_type = False
                if first_digit in ('1', '2', '3'):
                    line_type = 'patrimonial'
                elif first_digit in ('4', '5'): # Ingresos y Gastos
                    line_type = 'refundicion'
                
                if line_type:
                    debit = -balance if balance < 0 else 0.0
                    credit = balance if balance > 0 else 0.0
                    
                    line_vals.append((0, 0, {
                        'type': line_type,
                        'account_id': account.id,
                        'debit': debit,
                        'credit': credit,
                        'balance': balance, # Guardamos el balance original informativo
                        'amount_currency': balance_data['amount_currency'],
                        'currency_id': account.currency_id.id,
                        'final_id': self.id,
                    }))
        
        self.write({'line_ids': line_vals})
        return True

    def get_yearly_balance(self, account):
        self.ensure_one()
        
        date_end = self.date
        date_start = date_end + relativedelta(years=-1, days=+1)
        
        target_company_ids = self.env['res.company'].search([
            ('id', 'child_of', self.company_id.id)
        ]).ids
        
        if not target_company_ids:
            target_company_ids = [self.company_id.id]
        
        company_ids_tuple = tuple(target_company_ids)
        company_sql_str = str(company_ids_tuple).replace(',)', ')')

        saldo_inicial_query = f"""
            SELECT SUM(aml.debit - aml.credit)
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN account_journal aj ON am.journal_id = aj.id
            WHERE aml.account_id = %s 
              AND aml.company_id IN {company_sql_str}
              AND aml.date < %s 
              AND am.state = 'posted'
              AND (aj.is_unofficial_journal IS NULL OR aj.is_unofficial_journal = FALSE)
        """
        self.env.cr.execute(saldo_inicial_query, (account.id, date_start))
        saldo_inicial_result = self.env.cr.fetchone()
        saldo_inicial = saldo_inicial_result[0] if saldo_inicial_result and saldo_inicial_result[0] else 0.0

        movimiento_periodo_query = f"""
            SELECT SUM(aml.debit - aml.credit)
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN account_journal aj ON am.journal_id = aj.id
            WHERE aml.account_id = %s 
              AND aml.company_id IN {company_sql_str}
              AND aml.date >= %s AND aml.date <= %s 
              AND am.state = 'posted'
              AND (aj.is_unofficial_journal IS NULL OR aj.is_unofficial_journal = FALSE)
        """
        self.env.cr.execute(movimiento_periodo_query, (account.id, date_start, date_end))
        movimiento_periodo_result = self.env.cr.fetchone()
        movimiento_periodo = movimiento_periodo_result[0] if movimiento_periodo_result and movimiento_periodo_result[0] else 0.0

        balance = saldo_inicial + movimiento_periodo
        
        currency_query = f"""
            SELECT SUM(aml.amount_currency), aml.currency_id
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN account_journal aj ON am.journal_id = aj.id
            WHERE aml.account_id = %s 
              AND aml.company_id IN {company_sql_str}
              AND aml.date >= %s AND aml.date <= %s 
              AND am.state = 'posted'
              AND (aj.is_unofficial_journal IS NULL OR aj.is_unofficial_journal = FALSE)
            GROUP BY aml.currency_id LIMIT 1
        """
        self.env.cr.execute(currency_query, (account.id, date_start, date_end))
        currency_result = self.env.cr.fetchone()
        
        return {
            'balance': balance,
            'amount_currency': currency_result[0] if currency_result else 0.0,
            'currency_id': currency_result[1] if currency_result else False
        }