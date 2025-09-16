# purchase_requisition_remaining_qty/models/purchase_order.py
# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import UserError
from odoo.tools import float_compare
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("MÉTODO CREATE INTERCEPTADO. Verificando %d órdenes.", len(vals_list))
        
        for vals in vals_list:
            if vals.get('origin'):
                origin_name = vals.get('origin')
                
                requisition = self.env['purchase.requisition'].search([('name', '=', origin_name)], limit=1)
                if requisition:
                    _logger.info("Orden vinculada al requerimiento %s a través del campo 'origin'. Iniciando validación.", requisition.name)
                    
                    all_lines_completed = all(
                        float_compare(line.qty_ordered, line.product_qty, precision_rounding=line.product_uom_id.rounding) >= 0
                        for line in requisition.line_ids
                    )
                    
                    if all_lines_completed:
                        _logger.warning("BLOQUEADO: Intento de crear OC para requerimiento %s que ya está completado.", requisition.name)
                        raise UserError(
                            ("No se puede crear una nueva orden de compra porque el requerimiento "
                             "de origen (%s) ya ha sido comprado en su totalidad.") % (requisition.name)
                        )
                    else:
                        _logger.info("OK: El requerimiento %s no estaba completo. Se permite la creación.", requisition.name)

        # Si todas las validaciones pasan, se crean las órdenes.
        return super(PurchaseOrder, self).create(vals_list)