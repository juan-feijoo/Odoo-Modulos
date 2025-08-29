# -*- coding: utf-8 -*-
{
    'name': "Stock Unpack Validation",
    'summary': """
        Añade una validación para prevenir el desempaquetado de paquetes
        con cantidades de producto negativas.""",
    'description': """
        Este módulo sobrescribe el método 'unpack' del modelo 'stock.quant.package'
        para verificar que todos los productos dentro del paquete tengan una cantidad
        igual o mayor a cero antes de permitir la operación.
    """,
    'author': "Juan Martin Feijoo",
    'category': 'Inventory/Warehouse',
    'version': '18.0.1.0.0',
    'depends': [
        'stock',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}