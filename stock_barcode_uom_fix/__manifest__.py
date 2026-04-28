# -*- coding: utf-8 -*-
{
    'name': 'Stock Barcode UoM Fix',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Mantiene la Unidad de Medida (ej. Bultos) del pedido al escanear en la app de Código de Barras.',
    'description': """
        Este módulo parchea el modelo OWL de Código de Barras para que, al escanear un producto, 
        herede la UdM de la línea de demanda (stock.move) en lugar de forzar la UdM base del producto.
    """,
    'author': 'Outsourcearg',
    'depends': ['stock_barcode'],
    'data': [
        "views/stock_quant_package_view.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'stock_barcode_uom_fix/static/src/js/barcode_picking_model.js',
        ],
        'stock_barcode.assets_barcode': [
            'stock_barcode_uom_fix/static/src/js/barcode_picking_model.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'OEEL-1',
}