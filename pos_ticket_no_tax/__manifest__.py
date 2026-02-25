{
    'name': 'POS Ticket Sin IVA',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Quita el IVA en tickets no fiscales (sin factura)',
    'depends': ['point_of_sale', 'pos_sale', 'l10n_ar_pos_einvoice_ticket'], 
    'data': [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_ticket_no_tax/static/src/js/PaymentScreen.js',
            'pos_ticket_no_tax/static/src/js/Order.js',
            'pos_ticket_no_tax/static/src/js/Orderline.js',
            'pos_ticket_no_tax/static/src/xml/OrderReceipt.xml',
            'pos_ticket_no_tax/static/src/css/pos_receipt_no_tax.css',
        ],
    },
    'installable': True,
    'license': 'OEEL-1',
}