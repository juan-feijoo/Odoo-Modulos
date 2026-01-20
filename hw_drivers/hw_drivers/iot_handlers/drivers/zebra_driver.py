# -*- coding: utf-8 -*-
import logging
import socket
import os
from odoo.addons.hw_drivers.drivers import Driver
from odoo.addons.hw_drivers.controllers.proxy import proxy_drivers
_logger = logging.getLogger(__name__)
class ZebraUniversalDriver(Driver):
    """
    Driver Universal para Impresoras Zebra (USB y Red)
    Este driver se registra en la IoT Box y espera comandos con ZPL crudo.
    """
    connection_type = 'zebra_universal'
    def __init__(self, identifier, device):
        super(ZebraUniversalDriver, self).__init__(identifier, device)
        self.device_type = 'zebra_universal_printer'
        self.device_connection = 'custom'
        self.device_name = 'Zebra Universal Pinter'
        _logger.info("ZebraUniversalDriver inicializado: %s", self.device_name)
    @classmethod
    def supported(cls, device):
        # Este método es un poco "truco". Como queremos un driver manual/universal,
        # retornamos True para que siempre intente cargar si se instancia manualmente
        # o podemos hacer que detecte USBs específicos de Zebra.
        # Por simplicidad para tu caso híbrido (IP/USB), permitiremos que se cargue.
        return True
    def action(self, data):
        """
        Este método se ejecuta cuando Odoo llama a 'action_call_driver'.
        Recibe un diccionario 'data' con el ZPL y la configuración.
        """
        _logger.info("ZebraDriver: Recibida orden de impresión")
        zpl_content = data.get('zpl_content')
        connection_type = data.get('connection_type', 'ip') # 'ip' o 'usb'
        if not zpl_content:
            _logger.error("ZebraDriver: No llegó contenido ZPL")
            return {'status': 'error', 'message': 'No ZPL content'}
        try:
            if connection_type == 'ip':
                target_ip = data.get('iot_ip') # La IP de la IMPRESORA, no de la IoT Box
                port = int(data.get('iot_puerto', 9100))
                self._print_network(target_ip, port, zpl_content)
            elif connection_type == 'usb':
                # Ruta del dispositivo, ej: /dev/usb/lp0
                device_path = data.get('usb_device_path', '/dev/usb/lp0')
                self._print_usb(device_path, zpl_content)
            return {'status': 'success'}
        except Exception as e:
            _logger.exception("ZebraDriver: Error durante la impresión")
            return {'status': 'error', 'message': str(e)}
    def _print_network(self, ip, port, zpl):
        """Envía ZPL por Socket a la IP de la impresora"""
        _logger.info(f"Enviando ZPL a red {ip}:{port}")
        mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mysocket.settimeout(5) # Timeout de 5 segundos
        try:
            mysocket.connect((ip, port))
            # ZPL necesita enviarse como bytes
            if isinstance(zpl, str):
                zpl = zpl.encode('utf-8')
            mysocket.send(zpl)
        finally:
            mysocket.close()
    def _print_usb(self, path, zpl):
        """Escribe ZPL directamente en el archivo de dispositivo USB"""
        _logger.info(f"Enviando ZPL a USB {path}")
        if not os.path.exists(path):
            raise Exception(f"Dispositivo USB no encontrado en {path}")
        # En Linux, escribir a la impresora USB es como escribir a un archivo
        with open(path, 'wb') as printer:
            if isinstance(zpl, str):
                zpl = zpl.encode('utf-8')
            printer.write(zpl)