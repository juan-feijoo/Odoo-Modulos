# -*- coding: utf-8 -*-
{
    "name": "Purchase Requisition Remaining Qty",
    "version": "17.0.1.0.0",
    "category": "Tools",
    "summary": "Validacion de Requerimiento de compras",
    'description': """
        Este módulo mejora la funcionalidad estándar del Acuerdo de Compra.
        Cuando un usuario crea una Orden de Compra a partir de una línea del acuerdo, 
        el sistema calculará automáticamente (Cantidad Total - Cantidad Solicitada) y propondrá este importe restante,
        en lugar de la cantidad total.
    """,
    "depends": [
        "purchase_requisition",
    ],
    "data": [
        'views/purchase_order_view.xml',
    ],
    "assets": {},
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True
}