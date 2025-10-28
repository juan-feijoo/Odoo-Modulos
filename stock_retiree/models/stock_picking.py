# -*- coding: utf-8 -*-
from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_retirado_por_id = fields.Many2one(
        comodel_name='res.partner',
        string='Retirado por',
        help='Persona de contacto que retira físicamente la mercadería.',
        tracking=True # ¡Recomendado! Esto registrará los cambios en el chatter.
    )