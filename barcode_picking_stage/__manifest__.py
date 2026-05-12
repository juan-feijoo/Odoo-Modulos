{
    "name": "Flujo Personalizado Barcode: Prep y Repaso",
    "version": "18.0.1.0.0", # Asegúrate de poner 18.0
    "author": "OutSourceArg",
    "depends": ["stock_barcode", "stock"],
    "data": [
        "views/stock_picking_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "barcode_picking_stage/static/src/js/stock_barcode_patch.js",
            "barcode_picking_stage/static/src/xml/stock_barcode_patch.xml",
        ],
    },
    "installable": True,
    "license": "LGPL-3"
}