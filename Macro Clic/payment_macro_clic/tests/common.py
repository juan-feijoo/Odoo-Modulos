# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.payment.tests.common import PaymentCommon

class MacroClicCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.provider = cls._prepare_provider('macro_clic', update_values={
            'macro_clic_commerce_id': '12345',
            'macro_clic_api_key': 'secret',
            'macro_clic_phrase': 'phrase',
            'macro_clic_branch_id': '0000000000',
        })
        cls.notification_data = {
            'reference': cls.reference,
            'amount': str(cls.amount),
            'status': 'approved',
            'transaction_id': 'TX123',
            'signature': 'dummy_sig', # Will be patched or calculated in tests
        }
