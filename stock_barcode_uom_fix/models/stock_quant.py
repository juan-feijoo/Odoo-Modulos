# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # Campos visuales para mostrar en el paquete
    pack_custom_uom_id = fields.Many2one('uom.uom', string="UdM Empaque", compute="_compute_pack_custom_uom")
    pack_custom_qty = fields.Float(string="Cant. Empaque", compute="_compute_pack_custom_uom")

    @api.depends('quantity', 'product_id', 'package_id')
    def _compute_pack_custom_uom(self):
        for quant in self:
            # Por defecto, mostramos la base
            quant.pack_custom_uom_id = quant.product_uom_id
            quant.pack_custom_qty = quant.quantity

            # Si el quant está dentro de un paquete, buscamos cómo llegó ahí
            if quant.package_id:
                # Buscamos el stock.move.line (ya validado) que metió este producto en este paquete
                move_line = self.env['stock.move.line'].search([
                    ('result_package_id', '=', quant.package_id.id),
                    ('product_id', '=', quant.product_id.id),
                    ('state', '=', 'done')
                ], limit=1)

                if move_line and move_line.product_uom_id != quant.product_uom_id:
                    quant.pack_custom_uom_id = move_line.product_uom_id
                    # Convertimos la cantidad base a la cantidad del bulto
                    quant.pack_custom_qty = quant.product_uom_id._compute_quantity(
                        quant.quantity, 
                        move_line.product_uom_id
                    )