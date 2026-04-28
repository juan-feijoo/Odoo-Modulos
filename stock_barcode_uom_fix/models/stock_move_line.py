# -*- coding: utf-8 -*-
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    def write(self, vals):
        """ Propaga cambios de UdM del Remito a las Líneas. """
        res = super().write(vals)
        if 'product_uom' in vals and not self._context.get('skip_uom_sync'):
            for move in self:
                _logger.info("[UOM_FIX] Sincronizando Move -> Lines para move %s", move.id)
                move.move_line_ids.with_context(skip_uom_sync=True).write({
                    'product_uom_id': vals['product_uom']
                })
        return res

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('move_id'):
                move = self.env['stock.move'].browse(vals['move_id'])
                if move.exists():
                    if vals.get('product_uom_id') != move.product_uom.id:
                        _logger.info("[UOM_FIX] Corrigiendo UdM durante split/creación de paquete para Move %s", move.id)
                        vals['product_uom_id'] = move.product_uom.id

        # 2. Creación normal
        res = super().create(vals_list)
        return res

    def write(self, vals):
        """ Sincroniza cambios de UdM de la Línea hacia el Remito (Move). """
        res = super().write(vals)
        
        if 'product_uom_id' in vals and not self._context.get('skip_uom_sync'):
            for line in self:
                if line.move_id and line.move_id.product_uom.id != line.product_uom_id.id:
                    _logger.info("[UOM_FIX] Sincronizando Line -> Move %s: %s", line.move_id.id, line.product_uom_id.name)
                    line.move_id.with_context(skip_uom_sync=True).write({
                        'product_uom': line.product_uom_id.id
                    })
        return res