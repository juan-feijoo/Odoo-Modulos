# -*- coding: utf-8 -*-
{
    'name': 'POS Self Order Custom Layout',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Personalización de Self Order',
    'depends': ['pos_self_order'],
    'data': [],
    'assets': {
        'pos_self_order.assets': [
            'pos_self_order_custom_layout/static/src/scss/self_order_custom.scss',
            'pos_self_order_custom_layout/static/src/xml/product_info_popup.xml',
            'pos_self_order_custom_layout/static/src/xml/product_card.xml',
        ],
    },
    'installable': True,
    'license': 'OEEL-1',
}