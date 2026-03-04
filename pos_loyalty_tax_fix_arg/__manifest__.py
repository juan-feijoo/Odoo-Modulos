# -*- coding: utf-8 -*-
{
    'name': 'POS Loyalty Taxes Fix (Argentina)',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Fuerza que los descuentos del POS usen solo los impuestos de su producto (Evita Impuestos Internos negativos).',
    'description': """
        En Argentina, la AFIP rechaza facturas con Impuestos Internos en negativo. 
        Por defecto, Odoo copia los impuestos de los productos originales a la línea de descuento.
        Este módulo sobreescribe las líneas de recompensa en el POS para que usen exclusivamente 
        los impuestos definidos en el Producto de Servicio de la recompensa (ej. IVA 21%).
    """,
    'depends': ['point_of_sale', 'pos_loyalty', 'l10n_ar'],
    'data': [],
    'assets': {
        'point_of_sale._assets_pos':[
            'pos_loyalty_tax_fix_arg/static/src/overrides/orderline.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}