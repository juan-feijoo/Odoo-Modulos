# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import hashlib
import base64
import os
from werkzeug import urls

# Librerías criptográficas estándar en Odoo.sh
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from odoo import _, api, models
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.payment_macro_clic import const
from odoo.addons.payment_macro_clic.controllers.main import MacroClicController

_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _macro_clic_encrypt_aes(self, data, secret_key):
        """ Encripta un string usando AES-256-CBC con IV prefijado (Estándar PlusPagos) """
        if data is None:
            data = ""
            
        key_bytes = secret_key.encode('utf-8')
        # La llave debe ser de 32 bytes para AES-256
        key = key_bytes[:32].ljust(32, b'\0')
        
        # Generamos un IV aleatorio de 16 bytes (bloque AES)
        iv = os.urandom(16)
        
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data.encode('utf-8')) + padder.finalize()
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()
        
        # IMPORTANTE: Macro Click espera el IV (16 bytes) + los datos encriptados. 
        # 16 + 16 = 32 bytes -> 44 caracteres en Base64.
        combined_data = iv + encrypted_bytes
        return base64.b64encode(combined_data).decode('utf-8')

    def _get_client_ip(self):
        """ Obtener la IP pública real del cliente en Odoo.sh """
        if not request:
            return "127.0.0.1"
        
        forwarded_for = request.httprequest.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
            
        return request.httprequest.remote_addr

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'macro_clic':
            return res

        payload = self._macro_clic_prepare_request_payload()

        if self.provider_id.state == 'enabled':
            api_url = "https://botonpp.asjservicios.com.ar/" 
        else:
            api_url = "https://sandboxpp.asjservicios.com.ar/"

        return {
            'api_url': api_url,
            'url_params': payload,
        }

    def _macro_clic_prepare_request_payload(self):
        base_url = self.provider_id.get_base_url()
        return_url = urls.url_join(base_url, MacroClicController._return_url)

        # Formato: 2 decimales sin puntos. Ej: 150.50 -> "15050"
        amount_str = f"{self.amount:.2f}".replace('.', '')
        
        provider = self.provider_id
        secret_key = provider.macro_clic_secret_key.strip()
        hash_phrase = (provider.macro_clic_phrase or secret_key).strip()
        branch_id = provider.macro_clic_branch_id or ""
        
        client_ip = self._get_client_ip()
        
        # 1. Generar Hash: IP + Frase/SecretKey + GUID + Sucursal + Monto
        string_to_hash = f"{client_ip}{hash_phrase}{provider.macro_clic_commerce_id}{branch_id}{amount_str}"
        hash_value = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()

        # 2. Encriptar campos obligatorios (ahora con IV prefijado)
        enc_callback_success = self._macro_clic_encrypt_aes(return_url, secret_key)
        enc_callback_cancel = self._macro_clic_encrypt_aes(return_url, secret_key)
        enc_monto = self._macro_clic_encrypt_aes(amount_str, secret_key)
        enc_sucursal = self._macro_clic_encrypt_aes(branch_id, secret_key)

        payload = {
            'CallbackSuccess': enc_callback_success,
            'CallbackCancel': enc_callback_cancel,
            'Comercio': provider.macro_clic_commerce_id, # Cambiado a Mixed Case según pág 18
            'SucursalComercio': enc_sucursal,
            'Hash': hash_value,
            'TransaccionComercioId': self.reference,
            'Monto': enc_monto,
            'Producto[0]': f"Pago Orden {self.reference}",
            'MontoProducto[0]': amount_str, # Sin encriptar según manual
            'ClientData.NombreApellido': self.partner_name or 'Consumidor Final',
        }
        
        _logger.info("Macro Clic Payload generado para ref %s con IP %s y Monto %s", self.reference, client_ip, amount_str)
        return payload

    # === MÉTODOS DE RETORNO (WEBHOOK) ===
    def _get_tx_from_notification_data(self, provider_code, notification_data):
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'macro_clic' or len(tx) == 1:
            return tx

        reference = notification_data.get('TransaccionComercioId') 
        if not reference:
            raise ValidationError("Macro Clic: Datos recibidos sin referencia.")

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'macro_clic')])
        if not tx:
            raise ValidationError(f"Macro Clic: No se encontró transacción para la referencia {reference}.")
        return tx

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'macro_clic':
            return

        # Macro Click devuelve el estado en 'EstadoId' o 'Estado'
        payment_status = str(notification_data.get('EstadoId', ''))
        self.provider_reference = notification_data.get('TransaccionPlataformaId')

        # Mapeo según manual página 22
        if payment_status == '3': # 3 = REALIZADA
            self._set_done()
        elif payment_status in ['1', '2', '10']: # CREADA, EN_PAGO, PENDIENTE
            self._set_pending()
        elif payment_status in ['8', '9']: # CANCELADA, DEVUELTA
            self._set_canceled()
        elif payment_status in['4', '7', '11']: # RECHAZADA, EXPIRADA, VENCIDA
            self._set_error("Macro Clic: Pago rechazado o expirado.")
        else:
            _logger.warning("Macro Clic estado desconocido: %s", payment_status)
            self._set_error("Macro Clic: Estado desconocido.")