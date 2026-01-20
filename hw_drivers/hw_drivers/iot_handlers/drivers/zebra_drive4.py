# -*- coding: utf-8 -*-
import logging
from odoo.addons.hw_drivers.driver import Driver

_logger = logging.getLogger(__name__)

class ZebraUniversalDriver(Driver):
    """
    Driver Universal para Impresoras Zebra.
    Reemplaza al driver estándar para dispositivos Zebra USB.
    """
    connection_type = 'zebra_universal'

    def __init__(self, identifier, device):
        super(ZebraUniversalDriver, self).__init__(identifier, device)
        self.device_type = 'zebra_universal_printer' # Esto le dice a Odoo que use tu tipo personalizado
        self.device_connection = 'usb'
        self.device_name = 'Zebra Universal (Custom)'
        _logger.info("ZebraUniversalDriver: Tomando control del dispositivo %s", self.device_name)

    @classmethod
    def supported(cls, device):
        """
        Esta función determina si este driver se hace cargo del dispositivo.
        Buscamos Vendor ID de Zebra (0x0a5f) en dispositivos USB.
        """
        # Escaneo de dispositivos USB
        try:
            # 0x0a5f es el Vendor ID estándar de Zebra Technologies
            if device.get('vendor_id') == 0x0a5f:
                return True
        except Exception:
            pass
            
        # Si quisieras mantener soporte para IP manual, podrías dejar esto,
        # pero para que te aparezca automático por USB, lo de arriba es lo clave.
        return False

    def action(self, data):
        """
        Recibe la orden desde Odoo (ZPL crudo)
        """
        # Obtenemos la ruta del dispositivo directamente del objeto device que detectó la IoT Box
        # Esto es más seguro que pasarlo desde Odoo manualmente.
        device_path = self.device.get('path') or self.device.get('dev_path')
        
        # Si no lo encuentra en el objeto, usamos el que manda Odoo como respaldo
        if not device_path:
             device_path = data.get('usb_device_path')

        zpl_content = data.get('zpl_content')
        
        if not zpl_content:
            return {'status': 'error', 'message': 'No ZPL content'}
        
        if not device_path:
             return {'status': 'error', 'message': 'No device path found'}

        _logger.info(f"ZebraDriver: Imprimiendo en {device_path}")

        try:
            # Escritura directa al USB
            with open(device_path, 'wb') as printer:
                if isinstance(zpl_content, str):
                    zpl_content = zpl_content.encode('utf-8')
                printer.write(zpl_content)
            return {'status': 'success'}
        except Exception as e:
            _logger.exception("Error imprimiendo en Zebra USB")
            return {'status': 'error', 'message': str(e)}