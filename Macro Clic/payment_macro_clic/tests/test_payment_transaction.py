# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hashlib
from unittest.mock import patch

from odoo.tests import tagged
from odoo.addons.payment_macro_clic.tests.common import MacroClicCommon

@tagged('post_install', '-at_install')
class TestPaymentTransaction(MacroClicCommon):

    def test_processing_notification_data_confirms_transaction(self):
        """ Test that the transaction state is set to 'done' when the notification data indicate a
        successful payment. """
        tx = self._create_transaction(flow='redirect')
        
        # Calculate valid signature
        payload = self.notification_data.copy()
        payload['reference'] = tx.reference
        expected_string = f"{tx.reference}{payload['amount']}{payload['status']}{self.provider.macro_clic_phrase}"
        payload['signature'] = hashlib.sha256(expected_string.encode('utf-8')).hexdigest()

        tx._process_notification_data(payload)
        self.assertEqual(tx.state, 'done')

    def test_processing_notification_data_rejects_transaction(self):
        """ Test that the transaction state is set to 'error' when the status is unknown. """
        tx = self._create_transaction(flow='redirect')
        
        payload = self.notification_data.copy()
        payload.update({
            'reference': tx.reference,
            'status': 'rejected',
        })
        expected_string = f"{tx.reference}{payload['amount']}{payload['status']}{self.provider.macro_clic_phrase}"
        payload['signature'] = hashlib.sha256(expected_string.encode('utf-8')).hexdigest()

        tx._process_notification_data(payload)
        self.assertEqual(tx.state, 'error')
