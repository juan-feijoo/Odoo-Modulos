# -*- coding: utf-8 -*-
from odoo import models
from odoo.exceptions import UserError
from odoo.tools import float_compare

class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):

        
        remaining_qty = self.product_qty - self.qty_ordered

        if float_compare(remaining_qty, 0, precision_rounding=self.product_uom_id.rounding) <= 0:
            raise UserError(
                ("No se puede crear un pedido para el producto '%s' "
                 "porque la cantidad total requerida ya ha sido comprada.") %        (self.product_id.display_name)
            )
        res = super(PurchaseRequisitionLine, self)._prepare_purchase_order_line(
            name, product_qty, price_unit, taxes_ids
        )
        
        # La cantidad a sugerir es la restante que calculamos.
        # La función max() asegura que no propongamos un número negativo si algo sale mal.
        suggested_qty = max(0, remaining_qty)
        res['product_qty'] = suggested_qty

        return res