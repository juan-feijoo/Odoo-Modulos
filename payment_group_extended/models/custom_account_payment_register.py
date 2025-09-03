from odoo import models, fields

class CustomAccountPaymentRegister(models.TransientModel):
    _inherit = 'custom.account.payment.register'

    l10n_latam_check_issue_date = fields.Date(string="Fecha de emisión del cheque")

    def _create_payment_vals_from_wizard(self):
        vals = super()._create_payment_vals_from_wizard()

        vals['l10n_latam_check_issue_date'] = self.l10n_latam_check_issue_date
        
        return vals