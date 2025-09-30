# -*- coding: utf-8 -*-
{
    'name': "Fix: Balance en Tablero de Contabilidad (AR)",
    'summary': """
        Corrige el cálculo del balance en el tablero de contabilidad para
        diarios de tipo banco/efectivo, asegurando que muestre el saldo
        real del libro mayor, incluyendo operaciones misceláneas.
    """,
    'description': """
        Este módulo modifica el comportamiento del tablero de contabilidad (account_dashboard)
        para que el balance principal refleje el total de la cuenta contable asociada al diario,
        en lugar de excluir los asientos manuales.
    """,
    'author': "Outsource",
    'category': 'Accounting/Accounting',
    'version': '17.0.1.0.0',

    'depends': ['account'],

    'data': [],

    'installable': True,
    'application': False,
    'auto_install': False,
}