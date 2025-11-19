# -*- coding: utf-8 -*-
{
    'name': 'Automatizaciones de Ventas (Argentina)',
    'version': '18.0.1.0.0',
    'summary': 'Establece valores por defecto en facturas y pagos según la lista de precios seleccionada en el pedido de venta.',
    'description': """
        Este módulo personaliza el flujo de ventas para dos circuitos:
        - Transferencias: Asigna diario de facturación electrónica y términos de pago inmediato.
        - Efectivo: Asigna diario para comprobantes 'B' y términos de pago inmediato.
        Adicionalmente, establece el diario de cobro por defecto al registrar un pago.
    """,
    'author': 'OutsourceArg',
    'category': 'Sales/Localization',
    'depends': [
        'sale_management', 
        'account',         
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}