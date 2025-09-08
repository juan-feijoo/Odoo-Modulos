# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Cuenta Analítica por Defecto',
        help='Si se establece, esta cuenta analítica se asignará a los apuntes contables generados en este diario.'
    )