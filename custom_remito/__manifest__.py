# -*- coding: utf-8 -*-
{
    'name': "Custom remito sequence",
    'summary': """Custom sequence and printing for pre-printed delivery slips.""",
    'description': """
        This module adds a custom sequence for delivery slips (remitos)
        and allows choosing between standard Odoo printing and a header-less
        format for pre-printed paper.
    """,
    'author': "OutosourceArg",
    'website': "https://www.outsourcearg.com",
    'category': 'Inventory/Warehouse',
    'version': '18.0.1.0', 
    'depends': ['stock'],
    
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/stock_picking_views.xml',
        ],
    
    'installable': True,
}