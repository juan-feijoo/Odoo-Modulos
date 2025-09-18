# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.tools import float_compare

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    def _is_fully_ordered(self):
        self.ensure_one()
        if not self.line_ids:
            return False
        return all(
            float_compare(line.qty_ordered, line.product_qty, precision_rounding=line.product_uom_id.rounding) >= 0
            for line in self.line_ids
        )