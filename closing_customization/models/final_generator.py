# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import datetime

class FinalGenerator(models.Model):
    _inherit = 'final.generator'

    date = fields.Date(
        string='Fecha de cierre',
        compute='_compute_date',
        store=True,
        readonly=False,
        precompute=True
    )

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


    def _bypass_lock_date_and_execute(self, method_name):
        """
        Método auxiliar para quitar el bloqueo fiscal, ejecutar una acción
        y volver a poner el bloqueo.
        """
        company = self.company_id
        
        old_fiscal_lock = company.fiscalyear_lock_date
        old_period_lock = company.period_lock_date
        
        # 2. Abrimos el candado (ponemos False en las fechas)
        # Usamos sudo() porque un usuario normal quizás no tiene permiso para cambiar ajustes
        company.sudo().write({
            'fiscalyear_lock_date': False,
            'period_lock_date': False
        })
        
        try:
            # 3. Ejecutamos el método original (super)
            res = getattr(super(FinalGenerator, self), method_name)()
            return res
        finally:
            # 4. VOLVEMOS A CERRAR EL CANDADO (Importante: bloque finally para que ocurra sí o sí)
            company.sudo().write({
                'fiscalyear_lock_date': old_fiscal_lock,
                'period_lock_date': old_period_lock
            })

    def generar_asientos(self):
        """ Generar Refundición con Bypass de Bloqueo """
        
        res = self._bypass_lock_date_and_execute('generar_asientos')
        
        company = self.company_id
        old_fiscal_lock = company.fiscalyear_lock_date
        # Abrimos momentáneamente para el write
        if old_fiscal_lock and self.date and old_fiscal_lock >= self.date:
             company.sudo().write({'fiscalyear_lock_date': False})

        try:
            if self.refundicion and self.date and self.refundicion.date != self.date:
                self.refundicion.write({
                    'date': self.date,
                    'name': False 
                })
        finally:
             # Restauramos
             if old_fiscal_lock and self.date and old_fiscal_lock >= self.date:
                company.sudo().write({'fiscalyear_lock_date': old_fiscal_lock})
            
        return res

    def generar_patrimonial(self):
        """ Generar Patrimonial con Bypass de Bloqueo """
        
        res = self._bypass_lock_date_and_execute('generar_patrimonial')
        
        company = self.company_id
        old_fiscal_lock = company.fiscalyear_lock_date
        
        # Si hay bloqueo y molesta a nuestra fecha, lo quitamos para el write
        need_unlock = old_fiscal_lock and self.date and old_fiscal_lock >= self.date
        
        if need_unlock:
             company.sudo().write({'fiscalyear_lock_date': False})

        try:
            if self.patrimonial and self.date and self.patrimonial.date != self.date:
                self.patrimonial.write({
                    'date': self.date,
                    'name': False 
                })
        finally:
             if need_unlock:
                company.sudo().write({'fiscalyear_lock_date': old_fiscal_lock})
            
        return res

    def action_create_move(self):

        return super(FinalGenerator, self).action_create_move()

    def get_yearly_balance(self, account):
        self.ensure_one()
        date_end = self.date
        date_start = date_end + relativedelta(years=-1, days=1)
        target_company_ids = self.env['res.company'].search([('id', 'child_of', self.company_id.id)]).ids
        company_ids_tuple = tuple(target_company_ids)
        company_sql = str(company_ids_tuple).replace(',)', ')')
        is_result_account = account.code.startswith(('4', '5'))

        base_filters = f"""
            AND aml.account_id = %s
            AND aml.company_id IN {company_sql}
            AND am.state = 'posted'
            AND (aj.is_unofficial_journal IS NULL OR aj.is_unofficial_journal = FALSE)
        """
        saldo_inicial = 0.0
        if not is_result_account:
            saldo_inicial_query = f"""
                SELECT SUM(aml.debit - aml.credit)
                FROM account_move_line aml
                JOIN account_move am ON aml.move_id = am.id
                JOIN account_journal aj ON am.journal_id = aj.id
                WHERE aml.date < %s {base_filters} AND aj.type != 'situation'
            """
            self.env.cr.execute(saldo_inicial_query, (date_start, account.id))
            res_inicial = self.env.cr.fetchone()
            saldo_inicial = res_inicial[0] if res_inicial and res_inicial[0] else 0.0

        situation_filter = "" if is_result_account else "AND aj.type != 'situation'"
        movimiento_periodo_query = f"""
            SELECT SUM(aml.debit - aml.credit)
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN account_journal aj ON am.journal_id = aj.id
            WHERE aml.date >= %s AND aml.date <= %s {base_filters} {situation_filter}
        """
        self.env.cr.execute(movimiento_periodo_query, (date_start, date_end, account.id))
        res_periodo = self.env.cr.fetchone()
        movimiento_periodo = res_periodo[0] if res_periodo and res_periodo[0] else 0.0

        balance = saldo_inicial + movimiento_periodo
        currency_query = f"""
            SELECT SUM(aml.amount_currency), aml.currency_id
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN account_journal aj ON am.journal_id = aj.id
            WHERE aml.date >= %s AND aml.date <= %s {base_filters} {situation_filter}
            GROUP BY aml.currency_id LIMIT 1
        """
        self.env.cr.execute(currency_query, (date_start, date_end, account.id))
        currency_result = self.env.cr.fetchone()
        return {'balance': balance, 'amount_currency': currency_result[0] if currency_result else 0.0, 'currency_id': currency_result[1] if currency_result else False}