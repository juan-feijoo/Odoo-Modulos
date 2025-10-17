# -*- coding: utf-8 -*-
from odoo import models
from odoo.exceptions import UserError

class ArgentinianReportCustomHandler(models.AbstractModel):
    _inherit = 'l10n_ar.tax.report.handler'

    def _build_query(self, report, options, column_group_key):
        """
        Heredamos la función que construye el query de SQL para añadir nuestras
        columnas de base imponible directamente en la consulta.
        """
        query, params = super()._build_query(report, options, column_group_key)

        TaxGroup = self.env['account.tax.group']
        # Buscamos los grupos de impuestos por su código AFIP
        tax_group_10_5 = TaxGroup.search([('l10n_ar_vat_afip_code', '=', '4')], limit=1)
        tax_group_21 = TaxGroup.search([('l10n_ar_vat_afip_code', '=', '5')], limit=1)

        if not tax_group_10_5 or not tax_group_21:
            raise UserError("No se pudieron encontrar los grupos de impuestos para IVA 10.5% (código AFIP 4) o 21% (código AFIP 5). Verifique la configuración de la localización argentina.")

        new_fields = f"""
            , SUM(CASE WHEN "account_move_line".tax_group_id = {tax_group_10_5.id} THEN "account_move_line".tax_base_amount ELSE 0 END) AS gravado_10_5
            , SUM(CASE WHEN "account_move_line".tax_group_id = {tax_group_21.id} THEN "account_move_line".tax_base_amount ELSE 0 END) AS gravado_21
        """
       
        if 'SUM(account_move_line.balance) AS total' in query:
             query = query.replace(
                'SUM(account_move_line.balance) AS total',
                'SUM(account_move_line.balance) AS total' + new_fields
            )
        else:
            select_str = "SELECT %s AS column_group_key,"
            query = query.replace(select_str, select_str + new_fields.replace(',', '', 1))

        return query, params

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals, warnings=None):

        original_number_keys = list(self.number_keys)
        try:
            if 'gravado_10_5' not in self.number_keys:
                self.number_keys.append('gravado_10_5')
            if 'gravado_21' not in self.number_keys:
                self.number_keys.append('gravado_21')

            lines = super()._dynamic_lines_generator(report, options, all_column_groups_expression_totals, warnings=warnings)
        finally:
            self.number_keys = original_number_keys

        return lines