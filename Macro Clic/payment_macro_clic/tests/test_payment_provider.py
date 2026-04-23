# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged
from odoo.addons.payment_macro_clic.tests.common import MacroClicCommon

@tagged('post_install', '-at_install')
class TestPaymentProvider(MacroClicCommon):

    def test_supported_currencies(self):
        """ Test that Macro Clic only supports ARS. """
        supported_currencies = self.provider._get_supported_currencies()
        self.assertIn('ARS', supported_currencies.mapped('name'))
        self.assertEqual(len(supported_currencies), 1)

    def test_default_payment_method_codes(self):
        """ Test that the default payment method is macro_clic. """
        default_codes = self.provider._get_default_payment_method_codes()
        self.assertIn('macro_clic', default_codes)
