# /stock_barcode_product_temperature/__manifest__.py
{
    'name': 'Stock Barcode Product Temperature',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Agrega un campo de temperatura en la app de Código de Barras.',
    'author': 'Outsource',
    'depends': [
        'stock_barcode', 
    ],
    'data': [
        'views/stock_barcode_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OEEL-1',
}