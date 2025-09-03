from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    l10n_latam_check_issue_date = fields.Date(
        string="Fecha de emisión del cheque",
        tracking=True,  
        copy=False
    )