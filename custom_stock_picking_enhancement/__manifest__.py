# -*- coding: utf-8 -*-
{
    'name': 'Mejoras a Combinación de Remitos',
    'version': '18.0.1.0.0',
    'summary': 'Hereda y mejora la funcionalidad de combinar remitos.',
    'description': """
        Este módulo hereda del módulo 'stock_picking_grouping' para agregar:
        - Validación de propietario único al combinar remitos.
        - Asignación correcta del propietario al nuevo remito y sus movimientos.
        - Lógica mejorada para el campo 'Documento Origen'.
    """,
    'author': 'Juan Feijoo',
    'category': 'Inventory/Inventory',
    'depends': [
        "stock", 
        "odoo-mod-parche-stock_picking_grouping",
    ],
    'data': [
         'views/stock_move_line_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}