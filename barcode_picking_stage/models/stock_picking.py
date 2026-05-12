# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    preparador_id = fields.Many2one('res.users', string="Preparador", readonly=True, copy=False)
    fecha_preparacion = fields.Datetime(string="Fecha de Preparación", readonly=True, copy=False)
    revisor_id = fields.Many2one('res.users', string="Revisor de Repaso", readonly=True, copy=False)
    fecha_repaso = fields.Datetime(string="Fecha de Repaso", readonly=True, copy=False)

    def _get_stock_barcode_data(self):
        res = super()._get_stock_barcode_data()
        # Iteramos de forma segura en caso de que existan múltiples registros cacheados en el barcode
        if 'stock.picking' in res.get('records', {}):
            for picking_data in res['records']['stock.picking']:
                picking = self.browse(picking_data['id'])
                picking_data.update({
                    'preparador_id': picking.preparador_id.id if picking.preparador_id else False,
                    'revisor_id': picking.revisor_id.id if picking.revisor_id else False,
                    'flujo_doble_validacion': picking.picking_type_id.flujo_doble_validacion, # Enviamos la configuración
                })
        return res

    def action_barcode_finalizar_preparacion(self):
        self.ensure_one()
        self.write({
            'preparador_id': self.env.user.id,
            'fecha_preparacion': fields.Datetime.now(),
        })
        return True

    def action_barcode_iniciar_repaso(self):
        self.ensure_one()
        self.write({
            'revisor_id': self.env.user.id,
            'fecha_repaso': fields.Datetime.now(),
        })
        return True