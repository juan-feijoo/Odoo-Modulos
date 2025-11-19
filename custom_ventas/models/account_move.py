# -*- coding: utf-8 -*-
from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_force_register_payment(self):
        """
        Intercepta la acción de pago para preseleccionar el diario
        basado en la lista de precios de la venta original.
        """
        action = super(AccountMove, self).action_force_register_payment()

        # 2. Verificamos condiciones básicas
        if len(self) == 1 and self.invoice_origin:
            
            sale_order = self.env['sale.order'].search([('name', '=', self.invoice_origin)], limit=1)
            
            if sale_order:
                pricelist_journal_map = {
                    72: 67,   # Efectivo
                    71: 267   # Transferencia
                }
                
                current_pricelist_id = sale_order.pricelist_id.id
                if current_pricelist_id in pricelist_journal_map:

                    target_journal_id = pricelist_journal_map[current_pricelist_id]

                    if 'context' not in action:
                        action['context'] = {}

                    action['context']['default_journal_id'] = target_journal_id
                    action['context']['journal_id'] = target_journal_id

        return action