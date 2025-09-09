# -*- coding: utf-8 -*-
{
    "name": "Libro Mayor con CUIT",
    "version": "17.0.1.0.0",
    "category": "Accounting",
    "summary": "Agrega el campo CUIT en el reporte del Libro Mayor",
    "description": """Módulo personalizado que extiende el reporte de Libro Mayor (General Ledger)
                    para incluir el campo CUIT del partner en una columna adicional.
                    Requiere Odoo 17.0 o superior.
                    """,
    "author": 'Outsource Arg',
    "depends": [ "account_reports", 'l10n_ar',],
    "data": [
    ],
    "assets": {},
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True
}