# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError

class ArgentinianReportCustomHandler(models.AbstractModel):
    _inherit = 'l10n_ar.tax.report.handler'

    def _build_query(self, report, options, column_group_key):
        """
        Versión final que incluye el desglose de bases imponibles de IVA y el
        desglose de las percepciones de Ingresos Brutos por jurisdicción.
        """
        query, params = super()._build_query(report, options, column_group_key)

        # Lógica de valor condicional que asegura el signo correcto en Ventas y Compras.
        value_logic = """
            (CASE 
                WHEN COALESCE(nt.type_tax_use, bt.type_tax_use) = 'sale'
                THEN -("account_move_line".balance) 
                ELSE "account_move_line".balance 
            END)
        """

        # Añadimos los campos para las bases de IVA y las nuevas percepciones.
        new_fields = f"""
            , SUM(CASE 
                WHEN btg.l10n_ar_vat_afip_code = '4' 
                THEN {value_logic} ELSE 0 
            END) AS gravado_10_5
            , SUM(CASE 
                WHEN btg.l10n_ar_vat_afip_code = '5' 
                THEN {value_logic} ELSE 0 
            END) AS gravado_21
            , SUM(CASE 
                WHEN btg.l10n_ar_vat_afip_code = '6' 
                THEN {value_logic} ELSE 0 
            END) AS gravado_27
            
            , SUM(CASE 
                WHEN ntg.l10n_ar_vat_afip_code IS NULL AND ntg.l10n_ar_tribute_afip_code = '07' AND ntg.name->>'es_AR' ILIKE '%%Perc IIBB Catamarca%%'
                THEN {value_logic} ELSE 0 
            END) AS perc_iibb_catamarca
            
            , SUM(CASE 
                WHEN ntg.l10n_ar_vat_afip_code IS NULL AND ntg.l10n_ar_tribute_afip_code = '07' AND ntg.name->>'es_AR' ILIKE '%%Perc IIBB Santiago del Estero%%'
                THEN {value_logic} ELSE 0 
            END) AS perc_iibb_sgo

            , SUM(CASE 
                WHEN ntg.l10n_ar_vat_afip_code IS NULL AND ntg.l10n_ar_tribute_afip_code = '07' AND ntg.name->>'es_AR' ILIKE '%%Perc IIBB Neuquén%%'
                THEN {value_logic} ELSE 0 
            END) AS perc_iibb_neuquen
            
            , SUM(CASE 
                WHEN ntg.l10n_ar_vat_afip_code IS NULL AND ntg.l10n_ar_tribute_afip_code = '07' AND ntg.name->>'es_AR' ILIKE '%%Perc IIBB OTROS%%'
                THEN {value_logic} ELSE 0 
            END) AS perc_iibb_otros
            
        """
       
        anchor = 'SUM(account_move_line.balance) AS total'
        if anchor in query:
             query = query.replace(
                anchor,
                anchor + new_fields
            )
        else:
            raise UserError(_("No se pudo modificar la consulta SQL del reporte de IVA. El punto de anclaje no fue encontrado."))

        return query, params

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals, warnings=None):
        # Aquí registramos los nombres de nuestros nuevos campos para que Odoo los trate como números.
        original_number_keys = list(self.number_keys)
        try:
            # Campos de Gravado
            if 'gravado_10_5' not in self.number_keys: self.number_keys.append('gravado_10_5')
            if 'gravado_21' not in self.number_keys: self.number_keys.append('gravado_21')
            if 'gravado_27' not in self.number_keys: self.number_keys.append('gravado_27')
            
            # Campos de Percepciones IIBB
            if 'perc_iibb_catamarca' not in self.number_keys: self.number_keys.append('perc_iibb_catamarca')
            if 'perc_iibb_sgo' not in self.number_keys: self.number_keys.append('perc_iibb_sgo')
            if 'perc_iibb_neuquen' not in self.number_keys: self.number_keys.append('perc_iibb_neuquen')
            if 'perc_iibb_otros' not in self.number_keys: self.number_keys.append('perc_iibb_otros')

            lines = super()._dynamic_lines_generator(report, options, all_column_groups_expression_totals, warnings=warnings)
        finally:
            self.number_keys = original_number_keys

        return lines