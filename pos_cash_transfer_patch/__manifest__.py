{
    "name": "POS Cash Transfer",
    "version": "1.0",
    "depends": ["pos_cash_transfer","point_of_sale", "account","base"],
    "data": [
    ],
    "assets": {
        "point_of_sale._assets_pos":[
            "pos_cash_transfer_patch/static/src/js/cash_move_popup_patch.js",
        ],
    },
    "installable": True,
    "application": False,
}
