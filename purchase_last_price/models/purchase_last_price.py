# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        _logger.info("---[DEBUG]--- Iniciando onchange_product_id personalizado.")
        super(PurchaseOrderLine, self).onchange_product_id()

        if not self.product_id:
            _logger.info("---[DEBUG]--- No hay producto, terminando ejecución.")
            return

        _logger.info(f"---[DEBUG]--- Producto seleccionado: {self.product_id.display_name}")
        _logger.info(f"---[DEBUG]--- Precio unitario DESPUÉS de la lógica estándar de Odoo: {self.price_unit}")

        _logger.info("---[DEBUG]--- Buscando la última línea de compra...")
        last_po_line = self.env['purchase.order.line'].search([
            ('order_id.state', 'in', ['purchase', 'done']),
            ('product_id', '=', self.product_id.id),
            ('id', '!=', self._origin.id),
        ], order='date_approve desc, id desc', limit=1)

        if last_po_line:
            _logger.info(f"---[DEBUG]--- Última línea encontrada (ID: {last_po_line.id}) en la orden '{last_po_line.order_id.name}'.")
            _logger.info(f"---[DEBUG]--- Último precio encontrado: {last_po_line.price_unit}")
            
            self.price_unit = last_po_line.price_unit
            
            _logger.info(f"---[DEBUG]--- Precio unitario SOBRESCRITO a: {self.price_unit}")
        else:
            _logger.info("---[DEBUG]--- No se encontró ninguna compra anterior para este producto.")