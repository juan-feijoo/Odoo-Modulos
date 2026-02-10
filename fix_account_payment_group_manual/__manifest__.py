# -*- coding: utf-8 -*-
{
    'name': "Fix: Retenciones Manuales en Pagos Múltiples",
    'summary': "Soluciona error de moneda y numeración en retenciones manuales",
    'description': """
        Este módulo parchea 'account-payment-group' para:
        1. Asignar moneda automáticamente a retenciones creadas manualmente.
        2. Asegurar que las retenciones manuales se vinculen al pago y generen número.
    """,
    'author': "Juan Feijoo Outsource Arg",
    'website': "https://tusitio.com",
    'category': 'Accounting',
    'version': '17.0.1.0.0',
    'depends': [
        'account',
        'l10n_ar_withholding_ux', 
        'account-payment-group',  
    ],
    'data': [
        'views/report_fix.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}