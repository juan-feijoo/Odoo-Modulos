# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class MacroClicController(http.Controller):
    _return_url = '/payment/macro_clic/return'

    @http.route(_return_url, type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def macro_clic_return(self, **data):
        """ Procesa el retorno desde la web de Macro Clic """
        _logger.info("Respuesta recibida desde Macro Clic:\n%s", pprint.pformat(data))
        
        if data:
            request.env['payment.transaction'].sudo()._handle_notification_data(
                'macro_clic', data
            )

        # Redireccionar al usuario a la pantalla de estado de Odoo (éxito/fracaso)
        return request.redirect('/payment/status')