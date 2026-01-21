# -*- coding: utf-8 -*-
{
    'name': 'Retenciones Argentina - Base Acumulada en Certificado',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Muestra la base imponible acumulada en el certificado de retención de ganancias.',
    'author': 'Juan Feijoo Outsource Arg',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'l10n_ar',
        'l10n_ar_tax',
    ],
    'data': [
        'views/report_withholding_certificate_templates.xml',
        'views/account_payment_view.xml',
    ],
    'installable': True,
    'application': False,
}