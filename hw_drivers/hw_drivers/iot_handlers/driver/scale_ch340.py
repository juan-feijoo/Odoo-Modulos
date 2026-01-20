# -*- coding: utf-8 -*-
"""
Description: Serial Driver for CH341 devices in Odoo IoTBox
Author: [Your Name]
Date: 2024-XX-XX
Version: 0.1
"""

from collections import namedtuple
import logging
import re
import serial
import threading
import time

from odoo.addons.hw_drivers.controllers.proxy import proxy_drivers
from odoo.addons.hw_drivers.event_manager import event_manager
from odoo.addons.hw_drivers.iot_handlers.drivers.SerialBaseDriver import SerialDriver, SerialProtocol, serial_connection
from odoo.addons.hw_drivers.iot_handlers.drivers.SerialScaleDriver import ScaleDriver

_logger = logging.getLogger(__name__)

ACTIVE_SCALE = None
new_weight_event = threading.Event()
# Definir protocolo con los atributos necesarios
CH341Protocol = namedtuple('CH341Protocol', SerialProtocol._fields + ('zeroCommand', 'tareCommand', 'clearCommand', 'autoResetWeight'))

# Configurar el protocolo del dispositivo serial CH341
CH341SerialProtocol = CH341Protocol(
    name='CH341 Serial Protocol',
    baudrate=9600,  # Ajustar según el dispositivo CH341
    bytesize=serial.SEVENBITS,
    stopbits=serial.STOPBITS_TWO,
    parity=serial.PARITY_EVEN,
    timeout=0.5,
    writeTimeout=0.5,
    measureRegexp=re.compile(b'\x02.{2} (\d{6})\d{6}\r\n'),
    statusRegexp=None,
    commandDelay=0.1,
    measureDelay=0.1,
    newMeasureDelay=0.1,
    commandTerminator=b'\r\n',  # Terminador de comando adecuado para CH341
    measureCommand=b'PCOK',  # Comando para obtener lecturas del dispositivo
    zeroCommand=None,  # Sin comando de cero para este dispositivo
    tareCommand=None,
    clearCommand=None,
    emptyAnswerValid=False,
    autoResetWeight=False,
)


class CH341SerialDriver(ScaleDriver):
    """Driver para dispositivos seriales CH341 en Odoo IoTBox."""
    _protocol = CH341SerialProtocol

    def __init__(self, identifier, device):
        super(CH341SerialDriver, self).__init__(identifier, device)
        self.device_manufacturer = 'CH341 Device'
        _logger.info('Iniciando driver para dispositivo CH341 con identificador: %s', identifier)

    @classmethod
    def supported(cls, device):
        """Verifica si el dispositivo conectado es compatible con el protocolo CH341."""
        protocol = cls._protocol
        _logger.info("Probing device: %s", device)
        try:
            with serial_connection(device['identifier'], protocol, is_probing=True) as connection:
                _logger.info('Intentando conectar dispositivo %s con protocolo %s', device, protocol.name)
                connection.write(b'PCOK' + protocol.commandTerminator)  # Comando de prueba
                time.sleep(protocol.commandDelay)
                answer = connection.read(18)  # Lee la respuesta del dispositivo
                _logger.info('Respuesta: [%s] del dispositivo %s con protocolo %s', answer, device, protocol.name)
                
                # Verifica si la respuesta contiene los indicadores esperados
                if answer.find(b'') != -1 or answer.find(b'ERR') != -1:
                    _logger.info('Dispositivo %s es compatible con el protocolo %s', device, protocol.name)
                    return True
        except serial.serialutil.SerialTimeoutException:
            _logger.exception('Tiempo de espera agotado al conectar con %s utilizando el protocolo %s', device, protocol.name)
        except Exception:
            _logger.exception('Error al probar el dispositivo %s con el protocolo %s', device, protocol.name)
        
        return False
    
    def _read_weight(self):
        """Lee el peso de la balanza."""
        self._connection.reset_input_buffer()  # Limpia el buffer de entrada
        protocol = self._protocol
        answer = self._get_raw_response(self._connection)  # Lee la respuesta directamente
        #_logger.info("Respuesta recibida: %s", answer)
        match = re.search(self._protocol.measureRegexp, answer)
        #_logger.info(f"Respuesta recibida: {answer}")
        
        if match:
            weight = int(match.group(1))  # Captura el grupo 1 del regex que contiene el peso
            self.data = {
                'value': weight,
                'status': self._status
            }
            _logger.info(f"Peso capturado: {weight}")
        else:
            _logger.warning("No se pudo leer un peso válido de la respuesta: %s", answer)

    def _get_raw_response(self,connection):
        """Gets raw bytes containing the updated value of the device.

        :param connection: a connection to the device's serial port
        :type connection: pyserial.Serial
        :return: the raw response to a weight request
        :rtype: str
        """
        
        # Según el protocolo, la balanza envía 18 caracteres en cada respuesta
        expected_length = 18  # Número de caracteres que esperamos recibir
        answer = connection.read(expected_length)
        #_logger.info("Peso neto raw: %s", answer)
        # Si no se ha recibido nada o no coincide con la longitud esperada, log y retorno vacío
        if not answer or len(answer) < expected_length:
            _logger.warning("No se recibieron suficientes datos de la balanza: %s", answer)
            return b''
        # Retorna la respuesta completa
        return answer