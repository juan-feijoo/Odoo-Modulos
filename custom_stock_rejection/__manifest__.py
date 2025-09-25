# -*- coding: utf-8 -*-
{
    'name': "Gestión de Rechazos en Inventario",
    'summary': """
        Agrega un estado 'Rechazado' a las transferencias de inventario,
        facilitando el seguimiento de mercadería rechazada.""",
    'description': """
        Este módulo personaliza el flujo de trabajo de Inventario para Odoo 18.
        - Añade un nuevo estado 'Rechazado' a las recepciones (stock.picking).
        - Incluye un botón para mover una recepción a este estado.
        - La lógica interna maneja el rechazo como una cancelación de inventario.
        - Asegura la visibilidad de las transferencias rechazadas en las listas.
    """,
    'author': "OutsourceArg",
    'category': 'Inventory/Inventory',
    'version': '18.0.1.0.0',
    'depends': [
        'stock',
        'barcodes', 
    ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}