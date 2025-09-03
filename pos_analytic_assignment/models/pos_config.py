# -*- coding: utf-8 -*-
from odoo import models, fields

class PosConfig(models.Model):
    _inherit = 'pos.config'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Cuenta Analítica por Defecto',
        help='Esta cuenta analítica se asignará automáticamente a todas las facturas generadas desde este Punto de Venta.'
    )