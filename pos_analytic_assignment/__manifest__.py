# -*- coding: utf-8 -*-
{
    "name": "POS: Asignación Analítica por Sucursal",
    "version": "17.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Asigna una cuenta analítica a las facturas del PoS según la configuración de la sucursal.",
    "description": "Este módulo permite asignar cuentas analíticas a las facturas del Punto de Venta (PoS) en función de la configuración específica de cada sucursal.",
    "author": 'Juan Feijoo',
    "depends": [
        "point_of_sale",
        "account"
    ],
    "data": [
        'views/pos_config_view.xml',
    ],
    "assets": {},
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True
}