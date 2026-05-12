{
    'name': 'Custom Receipt AR (Notas de Crédito)',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Muestra Notas de Crédito en el recibo de pago',
    'depends': ['account', 'l10n_ar', 'l10n_ar_tax', 'l10n_ar_payment_bundle'],
    'data': [
        'views/report_payment_receipt.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}