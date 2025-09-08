# -*- coding: utf-8 -*-
{
    'name': 'Extensión de Pagos en Grupo',
    'version': '17.0.1.0.0',
    'summary': 'Agrega la fecha de emisión del cheque al proceso de pagos en grupo.',
    'author': 'Juan Feijoo',
    'category': 'Accounting/Localizations',
    'depends': [
        'account-payment-group',
    ],
    'data': [
        'views/custom_account_payment_register_view.xml',
        'views/account_payment_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}