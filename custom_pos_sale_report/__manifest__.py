{
    'name': 'Custom POS Sale Report Status',
    'version': '17.0.1.0.0',
    'summary': 'Agrega el estado de la factura a las órdenes de PDV en el informe de ventas.',
    'author': 'Outsource Arg',
    'website': 'https://www.outsourcearg.com',
    'category': 'Sales/Point of Sale',
    'depends': [
        'sale',
        'point_of_sale'
    ],
    'data': [
        'views/sale_report_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}