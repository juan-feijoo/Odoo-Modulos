from odoo import models, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_unofficial_journal = fields.Boolean(
        string="Diario No Fiscal (B)",
        help="Marcar si este diario se utiliza para operaciones no fiscales y sus movimientos deben ser excluidos del cierre oficial."
    )