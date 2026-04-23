# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import _, fields, models
from odoo.addons.payment_macro_clic import const

_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('macro_clic', "Macro Clic")], ondelete={'macro_clic': 'set default'}
    )

    macro_clic_commerce_id = fields.Char(
        string="Identificador de Comercio (GUID)",
        required_if_provider='macro_clic',
        help="Ej: 6f469e7c-8947-4572-a239-3e954a176c35"
    )
    macro_clic_secret_key = fields.Char(
        string="Secret Key",
        required_if_provider='macro_clic',
        groups='base.group_system',
        help="Clave para encriptación AES. Ej: DUBIDABA_fa3836..."
    )
    macro_clic_phrase = fields.Char(
        string="Frase",
        required_if_provider='macro_clic',
        groups='base.group_system',
        help="Frase para generar el Hash."
    )
    macro_clic_branch_id = fields.Char(
        string="Sucursal",
        default="",
        help="Dejar vacío si no aplica."
    )
    macro_clic_ente_code = fields.Char(
        string="Código de Ente",
        help="Ej: 795201 (Para modalidad Botón Simple)"
    )

    def _get_supported_currencies(self):
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'macro_clic':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies

    def _get_default_payment_method_codes(self):
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'macro_clic':
            return default_codes
        return const.DEFAULT_PAYMENT_METHOD_CODES