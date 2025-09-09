# -*- coding: utf-8 -*-
from odoo import models
import logging

_logger = logging.getLogger(__name__)

class AccountReport(models.Model):
    _inherit = 'account.report'

    def get_expanded_lines(self, options, line_id, *args, **kwargs):
        """
        Hereda el método que se ejecuta al expandir una cuenta en el Libro Mayor
        para inyectar el CUIT del partner en la columna correspondiente.
        """
        lines = super().get_expanded_lines(options, line_id, *args, **kwargs)

        for line in lines:
            if line.get('caret_options') == 'account.move.line':
                try:
                    aml_id_str = line['id'].split('~account.move.line~')[-1]
                    aml_id = int(aml_id_str)
                    
                    move_line = self.env['account.move.line'].browse(aml_id)
                    
                    if move_line and move_line.partner_id:
                        cuit = move_line.partner_id.vat or ''

                        for column in line.get('columns', []):
                            if column.get('expression_label') == 'cuit':
                                column['name'] = cuit
                                break
                                
                except (ValueError, IndexError, KeyError) as e:
                    _logger.error(f"Error al procesar el CUIT para la línea {line.get('id')}: {e}")

        return lines