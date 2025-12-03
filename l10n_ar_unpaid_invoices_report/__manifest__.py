# -*- coding: utf-8 -*-
{
    'name': 'Reporte Excel Facturas Impagas (Detallado)',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Reporting',
    'summary': 'Genera un Excel de facturas de cliente no pagadas con detalle de productos',
    'description': """
        Este módulo agrega un asistente en Contabilidad > Reportes
        para descargar un Excel con:
        - Facturas de Cliente Impagas (o parciales)
        - Detalle de líneas de producto
        - Filtro por fechas
    """,
    'author': 'OutsoruceArg',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/unpaid_invoice_report_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}