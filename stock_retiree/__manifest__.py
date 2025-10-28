# -*- coding: utf-8 -*-
{
    'name': 'Personalización de Picking: Retirado Por',
    'version': '17.0.1.0.0',
    'summary': 'Agrega un campo para registrar quién retira el pedido en los documentos de salida.',
    'description': """
        Este módulo personaliza el modelo stock.picking para:
        - Añadir un campo "Retirado por" (Many2one a res.partner).
        - Mostrar este campo en el formulario de Albaranes.
        - Limitar la visibilidad del campo a las compañías con ID 2 y 3.
        - Incluir la información en los reportes de Picking y Albarán de Entrega.
    """,
    'author': 'OutsourceArg/juan',
    'category': 'Inventory/Inventory',
    'depends': [
        'stock', 
    ],
    'data': [
        'views/stock_picking_views.xml',
        'reports/report_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}