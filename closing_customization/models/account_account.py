# models/account_account.py
from odoo import models, fields

class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_unofficial_account = fields.Boolean(
        string="Cuenta No Fiscal (B)",
        help="Marcar si esta cuenta se utiliza para operaciones no fiscales y debe ser excluida del cierre oficial."
    )