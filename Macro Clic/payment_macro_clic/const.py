# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tools import LazyTranslate
_lt = LazyTranslate(__name__)

# Monedas soportadas por Macro Clic
SUPPORTED_CURRENCIES = ['ARS']

# Método de pago por defecto (el que crearemos en data)
DEFAULT_PAYMENT_METHOD_CODES = {
    'macro_clic',
}

# Mapeo de estados de Macro Clic a estados de Odoo
TRANSACTION_STATUS_MAPPING = {
    'pending': ('pending',),
    'done': ('approved', '00'),
    'canceled': ('cancelled', 'null'),
    'error': ('rejected', 'Error'),
}

# Mapeo de mensajes de error
ERROR_MESSAGE_MAPPING = {
    'rejected': _lt("El pago fue rechazado por el banco. Por favor, verifique los datos de su tarjeta."),
    'expired': _lt("La sesión de pago ha expirado."),
    'insufficient_funds': _lt("No tiene fondos suficientes para completar la operación."),
}