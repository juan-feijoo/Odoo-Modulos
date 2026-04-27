# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import datetime
import logging

_logger = logging.getLogger(__name__)

class FinalGenerator(models.Model):
    _inherit = 'final.generator'

    date = fields.Date(
        string='Fecha de cierre',
        compute='_compute_date',
        store=True,
        readonly=False,
        precompute=True
    )
    
    # NUEVO CAMPO: Permitimos seleccionar el diario.
    journal_id = fields.Many2one(
        'account.journal',
        string='Diario de Cierre',
        domain="[('type', '=', 'general'), ('company_id', '=', company_id)]",
        required=True,
        default=lambda self: self._default_journal()
    )

    def _default_journal(self):
        # Buscamos por defecto el primer diario de operaciones varias
        company_id = self.env.company.id
        return self.env['account.journal'].search([
            ('type', '=', 'general'), 
            ('company_id', '=', company_id)
        ], limit=1)

    @api.depends('year', 'company_id')
    def _compute_date(self):
        for record in self:
            if not record.year:
                record.date = False
                continue
            try:
                year_int = int(record.year)
                company = record.company_id or self.env.company
                last_month = int(company.fiscalyear_last_month) if company.fiscalyear_last_month else 12
                last_day = company.fiscalyear_last_day if company.fiscalyear_last_day else 31
                record.date = datetime.date(year_int, last_month, 1) + relativedelta(day=last_day)
            except (ValueError, TypeError):
                record.date = datetime.date(int(record.year), 12, 31)

    # =====================================================================
    # OVERRIDE TOTAL: IGNORAMOS EL MÓDULO PADRE PARA EVITAR EL ERROR DE ODOO
    # =====================================================================

    def generar_asientos(self):
        """ Override de Refundición """
        self.ensure_one()
        company = self.company_id
        old_fiscal_lock = company.fiscalyear_lock_date
        
        if not self.line_ids:
            raise ValidationError("No hay líneas contables para generar los asientos.")

        # Bypass de seguridad fiscal
        if old_fiscal_lock and self.date and old_fiscal_lock >= self.date:
             company.sudo().write({'fiscalyear_lock_date': False})

        try:
            # 1. Limpiamos asiento previo si existe
            if self.refundicion:
                self.refundicion.button_draft()
                # Odoo 17 permite borrar asientos en borrador si no pertenecen a una secuencia bloqueada
                self.refundicion.unlink()

            # 2. Cuenta de contrapartida (Resultados)
            cuenta_contrapartida = self.env['account.account'].search([
                ('code', '=', '3.3.1.01.010'),  # Código quemado en el módulo original
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            
            if not cuenta_contrapartida:
                raise ValidationError("No se encontró la cuenta de contrapartida configurada (3.3.1.01.010).")

            # 3. Armamos las líneas
            if self.refundicion_line_ids:
                lineas_refundicion = []
                total_debito = 0
                total_credito = 0
                
                for linea in self.refundicion_line_ids:
                    lineas_refundicion.append((0, 0, {
                        'account_id': linea.account_id.id,
                        'name': f"Cierre refundición {self.year}",
                        'debit': linea.debit,
                        'credit': linea.credit,
                    }))
                    total_debito += linea.debit
                    total_credito += linea.credit
                
                if total_debito > total_credito:
                    lineas_refundicion.append((0, 0, {
                        'account_id': cuenta_contrapartida.id,
                        'name': f"Contrapartida refundición {self.year}",
                        'credit': total_debito - total_credito,
                    }))
                elif total_credito > total_debito:
                    lineas_refundicion.append((0, 0, {
                        'account_id': cuenta_contrapartida.id,
                        'name': f"Contrapartida refundición {self.year}",
                        'debit': total_credito - total_debito,
                    }))
                
                # 4. CREAMOS EL ASIENTO CON NUESTRO DIARIO CORRECTO DIRECTAMENTE
                asiento_refundicion = self.env['account.move'].create({
                    'move_type': 'entry',
                    'date': self.date,
                    'ref': f"Cierre Refundición {self.year}",
                    'journal_id': self.journal_id.id, # <--- LA MAGIA ESTÁ AQUÍ
                    'line_ids': lineas_refundicion,
                    'company_id': self.company_id.id,
                })
                asiento_refundicion.action_post()
                self.refundicion = asiento_refundicion

            self.total_refundicion = sum(self.refundicion_line_ids.mapped('balance'))
            self.action_create_move()
            
        finally:
             # Restauramos bloqueo
             if old_fiscal_lock and self.date and old_fiscal_lock >= self.date:
                company.sudo().write({'fiscalyear_lock_date': old_fiscal_lock})

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {
                'title': 'Asientos generados',
                'message': 'Los asientos contables se han generado correctamente.',
                'sticky': False,
            }
        }

    def generar_patrimonial(self):
        """ Override de Patrimonial """
        self.ensure_one()
        company = self.company_id
        old_fiscal_lock = company.fiscalyear_lock_date
        
        if old_fiscal_lock and self.date and old_fiscal_lock >= self.date:
             company.sudo().write({'fiscalyear_lock_date': False})

        try:
            if self.patrimonial:
                self.patrimonial.button_draft()
                self.patrimonial.unlink()

            if self.patrimonial_line_ids:
                lineas_patrimonial = []
                
                for linea in self.patrimonial_line_ids:
                    # Lógica original del módulo base
                    curr_id = linea.account_id.currency_id.id if linea.account_id.currency_id.id else linea.company_currency_id.id
                    amt_curr = -1 * linea.amount_currency if linea.account_id.currency_id.id == linea.company_currency_id.id else -1 * linea.balance
                    
                    lineas_patrimonial.append((0, 0, {
                        'account_id': linea.account_id.id,
                        'name': f"Cierre patrimonial {self.year}",
                        'currency_id': curr_id,
                        'amount_currency': amt_curr,
                        'debit': linea.debit,
                        'credit': linea.credit,
                    }))
                            
                asiento_patrimonial = self.env['account.move'].create({
                    'move_type': 'entry',
                    'date': self.date,
                    'ref': f"Cierre Patrimonial {self.year}",
                    'journal_id': self.journal_id.id, # <--- LA MAGIA ESTÁ AQUÍ TAMBIÉN
                    'line_ids': lineas_patrimonial,
                    'company_id': self.company_id.id,
                })
                asiento_patrimonial.action_post()
                self.patrimonial = asiento_patrimonial
        finally:
             if old_fiscal_lock and self.date and old_fiscal_lock >= self.date:
                company.sudo().write({'fiscalyear_lock_date': old_fiscal_lock})

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {
                'title': 'Asientos generados',
                'message': 'Los asientos contables se han generado correctamente.',
                'sticky': False,
            }
        }

    # =====================================================================
    # MANTENEMOS TU LÓGICA EXCELENTE DE CÁLCULO DE SALDOS
    # =====================================================================

    def get_yearly_balance(self, account):
        self.ensure_one()
        date_end = self.date
        
        fiscal_dates = self.company_id.compute_fiscalyear_dates(date_end)
        date_start = fiscal_dates.get('date_from') or (date_end + relativedelta(years=-1, days=1))

        target_company_ids = tuple(self.env['res.company'].search([('id', 'child_of', self.company_id.id)]).ids)
        is_result_account = account.code.startswith(('4', '5'))

        base_query = """
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN account_journal aj ON am.journal_id = aj.id
            WHERE aml.account_id = %(account_id)s
              AND aml.company_id IN %(company_ids)s
              AND am.state = 'posted'
              AND (aj.is_unofficial_journal IS NULL OR aj.is_unofficial_journal = FALSE)
              AND aj.type != 'situation'
        """

        params = {
            'account_id': account.id,
            'company_ids': target_company_ids,
            'date_start': date_start,
            'date_end': date_end,
        }

        saldo_inicial = 0.0
        if not is_result_account:
            saldo_inicial_query = f"SELECT SUM(aml.debit - aml.credit) {base_query} AND aml.date < %(date_start)s"
            self.env.cr.execute(saldo_inicial_query, params)
            res_inicial = self.env.cr.fetchone()
            saldo_inicial = res_inicial[0] if res_inicial and res_inicial[0] else 0.0

        movimiento_periodo_query = f"SELECT SUM(aml.debit - aml.credit) {base_query} AND aml.date >= %(date_start)s AND aml.date <= %(date_end)s"
        self.env.cr.execute(movimiento_periodo_query, params)
        res_periodo = self.env.cr.fetchone()
        movimiento_periodo = res_periodo[0] if res_periodo and res_periodo[0] else 0.0

        balance = saldo_inicial + movimiento_periodo

        currency_id = account.currency_id.id or self.company_id.currency_id.id
        params['currency_id'] = currency_id
        
        currency_query = f"SELECT SUM(aml.amount_currency) {base_query} AND aml.date >= %(date_start)s AND aml.date <= %(date_end)s AND aml.currency_id = %(currency_id)s"
        self.env.cr.execute(currency_query, params)
        currency_result = self.env.cr.fetchone()
        amount_currency = currency_result[0] if currency_result and currency_result[0] else 0.0

        return {
            'balance': balance, 
            'amount_currency': amount_currency, 
            'currency_id': currency_id
        }