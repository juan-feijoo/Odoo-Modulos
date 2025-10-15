# -*- coding: utf-8 -*-
{
    'name': 'Personalización de Remitos para Argentina',
    'version': '18.0.1.0.0',
    'summary': 'Agrega campos de Transporte, Chofer, Despachante y otros datos al albarán.',
    'author': 'OutSource Arg',
    'category': 'Inventory/Delivery',
    'depends': [
        'stock', # Dependencia del módulo de Inventario
        'account', # Dependencia para acceder a datos de facturas
        'sale_management', # Dependencia para acceder a la Orden de Venta
    ],
    'data': [
        'views/stock_picking_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}