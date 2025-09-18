# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _check_requisition_status(self):
        for order in self:
            if order.requisition_id and order.requisition_id._is_fully_ordered():
                raise UserError(_(
                    "La operación no puede continuar porque el acuerdo de origen '%s' ya ha sido comprado en su totalidad."
                ) % (order.requisition_id.name,))

    @api.model_create_multi
    def create(self, vals_list):
        orders = super(PurchaseOrder, self).create(vals_list)
        try:
            orders._check_requisition_status()
        except UserError:
            raise
        return orders

    def button_confirm(self):
        self._check_requisition_status()
        for order in self:
            if not order.requisition_id:
                continue
            for line in order.order_line:
                pr_line = order.requisition_id.line_ids.filtered(
                    lambda l: l.product_id == line.product_id
                )
                if not pr_line:
                    continue
                pr_line = pr_line[0]
                remaining_qty_before_confirm = pr_line.product_qty - pr_line.qty_ordered
                if float_compare(line.product_qty, remaining_qty_before_confirm, precision_rounding=line.product_uom.rounding) > 0:
                    raise UserError(_(
                        "La cantidad para el producto '%(product)s' excede la cantidad restante del acuerdo '%(requisition)s' (restante: %(qty_remaining)s)."
                    ) % {
                        'product': line.product_id.display_name,
                        'requisition': pr_line.requisition_id.name,
                        'qty_remaining': remaining_qty_before_confirm,
                    })
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.requisition_id and order.requisition_id._is_fully_ordered():
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': _("¡Excelente! Has completado todas las compras para el requerimiento %s.") % (order.requisition_id.name,),
                        'type': 'rainbow_man',
                    }
                }
        return res