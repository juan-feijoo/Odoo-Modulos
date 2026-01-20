# -*- coding: utf-8 -*-
# Driver Universal para impresoras Zebra que soportan lenguaje ZPL.
# Este driver es flexible y puede operar por dos métodos de conexión:
# 1. Red (IP): Envía ZPL a través de un socket a la IP y puerto de la impresora. (Recomendado)
# 2. USB Directo: Escribe el ZPL directamente al archivo de dispositivo USB en la Pi. (Contingencia)

import logging
import socket
from odoo.addons.delivery_iot.iot_handlers.driver import Driver

_logger = logging.getLogger(__name__)

class ZebraUniversalDriver(Driver):
    """
    Driver Universal para impresoras Zebra (ZPL).
    Maneja de forma inteligente la comunicación por Red (IP) o por USB
    basándose en los datos recibidos desde Odoo.
    """
    supported_devices = {
        'zebra_universal_printer': 'Impresora Zebra (Universal)',
    }

    def action(self, data):
        """
        Punto de entrada principal. Orquesta la impresión según el tipo de conexión.
        """
        zpl_content = data.get('zpl_content')
        if not zpl_content:
            _logger.error('Driver Universal: No se recibió contenido ZPL.')
            return {'status': 'error', 'message': 'No ZPL content'}

        connection_type = data.get('connection_type')
        if connection_type == 'ip':
            return self._print_via_ip(zpl_content, data)
        elif connection_type == 'usb':
            return self._print_via_usb(zpl_content, data)
        else:
            _logger.error(f"Driver Universal: Tipo de conexión no especificado o desconocido: {connection_type}")
            return {'status': 'error', 'message': 'Connection type not specified'}

    def _print_via_ip(self, zpl_content, data):
        """Maneja la impresión a través de la red."""
        device_ip = self.device_ip
        port = int(data.get('port', 9100))
        
        _logger.info(f"Driver Universal [IP]: Enviando ZPL a {device_ip}:{port}")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)
                sock.connect((device_ip, port))
                sock.sendall(zpl_content.encode('utf-8'))
                _logger.info(f"Driver Universal [IP]: ZPL enviado correctamente a {device_ip}.")
                return {'status': 'success'}
        except Exception as e:
            _logger.error(f"Driver Universal [IP]: Error inesperado: {e}")
            return {'status': 'error', 'message': f'{e}'}

    def _print_via_usb(self, zpl_content, data):
        """Maneja la impresión a través de una conexión USB directa."""
        device_path = data.get('device_path', '/dev/usb/lp0')

        _logger.info(f"Driver Universal [USB]: Escribiendo ZPL en {device_path}")
        try:
            with open(device_path, "wb") as printer_file:
                printer_file.write(zpl_content.encode('utf-8'))
            _logger.info(f"Driver Universal [USB]: ZPL escrito correctamente en {device_path}.")
            return {'status': 'success'}
        except Exception as e:
            _logger.error(f"Driver Universal [USB]: Error inesperado: {e}")
            return {'status': 'error', 'message': f'{e}'}