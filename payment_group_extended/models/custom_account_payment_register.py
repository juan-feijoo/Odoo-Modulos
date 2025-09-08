from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError

class CustomAccountPaymentRegister(models.TransientModel):
    _inherit = 'custom.account.payment.register'

    l10n_latam_check_issue_date = fields.Date(string="Fecha de emisión del cheque")


    def _create_payment_vals_from_wizard(self):
        vals = super()._create_payment_vals_from_wizard()
        vals['l10n_latam_check_issue_date'] = self.l10n_latam_check_issue_date
        return vals

    @api.constrains('l10n_latam_check_issue_date', 'payment_method_code')
    def _check_check_issue_date_required(self):
        for wizard in self:
            if wizard.payment_method_code == 'new_third_party_checks' and not wizard.l10n_latam_check_issue_date:
                raise ValidationError(_("La fecha de emisión del cheque es obligatoria cuando el método de pago es 'Nuevo Cheque de Tercero'."))