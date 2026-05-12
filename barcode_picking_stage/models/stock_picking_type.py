# -*- coding: utf-8 -*-
from odoo import models, fields

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    flujo_doble_validacion = fields.Boolean(
        string="Flujo de Código de Barras: Prep. y Repaso", 
        default=False,
        help="Habilita los botones de 'Finalizar Preparación' e 'Iniciar Repaso' en la app de Código de Barras."
    )