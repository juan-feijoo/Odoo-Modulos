# custom_stock_history/__manifest__.py
{
    'name': 'Histórico de Stock Diario',
    'version': '17.0.1.0.0',
    'summary': 'Añade una vista de histórico de stock diario con saldos acumulados.',
    'author': 'OutsourceArg',
    'category': 'Inventory/Reporting',
    'depends': [
        'stock',  # Dependemos del módulo de Inventario
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/daily_stock_history_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}