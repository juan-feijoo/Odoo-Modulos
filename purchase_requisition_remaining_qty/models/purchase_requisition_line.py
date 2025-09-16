# -*- coding: utf-8 -*-
from odoo import models
from odoo.exceptions import UserError
from odoo.tools import float_compare

class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        
        remaining_qty = self.product_qty - self.qty_ordered


        suggested_qty = max(0, remaining_qty)

        res = super(PurchaseRequisitionLine, self)._prepare_purchase_order_line(
            name, product_qty, price_unit, taxes_ids
        )
        
        res['product_qty'] = suggested_qty

        return res