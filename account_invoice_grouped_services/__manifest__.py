# -*- coding: utf-8 -*-
{
    'name': 'Factura de Servicios Agrupada por Sección',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Agrupa los montos de servicios por sección en el PDF de la factura.',
    'description': """
        Este módulo crea un nuevo reporte PDF para Facturas.
        Unifica y suma los montos de los servicios que se encuentran debajo de una Sección,
        mostrando en el PDF únicamente el nombre de la Sección y el subtotal sumado.
        Ideal para facturación de servicios complejos.
    """,
    'author': 'Outsource Juan',
    'depends': ['account', 'l10n_ar', 'sale'],
    'data':[
        'report/invoice_services_report.xml',
        'report/sale_services_report.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}