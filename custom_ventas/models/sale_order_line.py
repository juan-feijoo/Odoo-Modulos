# -*- coding: utf-8 -*-
from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id_update_taxes(self):
        if not self.pricelist_id:
            return

        # Si la lista de precios es 'Efectivo', quitamos todos los impuestos.
        if self.pricelist_id.name == 'Efectivo':
            for line in self.order_line:
                line.tax_id = [(5, 0, 0)]
        else:
            # Para CUALQUIER OTRA lista de precios, asignamos el impuesto específico con ID 64.
            for line in self.order_line:
                # El comando (6, 0, [IDs]) reemplaza los registros existentes en la relación
                # con la nueva lista de IDs. En este caso, solo el ID 64.
                # Asegúrate de que el impuesto con ID 64 exista en tu base de datos.
                line.tax_id = [(6, 0, [64])]

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'pricelist_id' in vals:
            for order in self:
                order._onchange_pricelist_id_update_taxes()
        return res