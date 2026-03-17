{
    'name': 'Reporte de Ventas por Proveedor',
    'version': '17.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Agrega el proveedor principal a los reportes de Ventas y Punto de Venta',
    'description': """
        Añade el campo 'Proveedor Principal' en los productos y permite agrupar por este
        campo en los análisis de Ventas (sale.report) y Punto de Venta (report.pos.order).
    """,
    'author': 'Tu Nombre/Empresa',
    'depends':[
        'product',
        'purchase',
        'sale',
        'point_of_sale',
        'pos_sale'
    ],
    'data':[
        'views/sale_report_views.xml',
        'views/pos_order_report_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}