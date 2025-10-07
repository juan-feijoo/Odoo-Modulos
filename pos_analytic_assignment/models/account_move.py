# -*- coding: utf-8 -*-
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        _logger.info("Módulo Analítico: Se crearon asientos con IDs %s. Verificando...", moves.ids)

        for move in moves:
            journal = move.journal_id
            analytic_account = journal.analytic_account_id
            
            if journal.type == 'sale' and analytic_account:
                _logger.info("Asiento %s usa el diario de ventas '%s' que tiene la cuenta analítica '%s'. Aplicando...", move.name, journal.name, analytic_account.name)
                
                for line in move.line_ids:
                    if not line.analytic_distribution:
                        _logger.info("-> Asignando a la línea '%s' (Cuenta: %s)", line.name, line.account_id.code)
                        line.analytic_distribution = {
                            str(analytic_account.id): 100.0
                        }
            else:
                _logger.info("Asiento %s (Diario: %s, Tipo: %s) no cumple los requisitos. Se ignora.", move.name, journal.name, journal.type)
        
        return moves