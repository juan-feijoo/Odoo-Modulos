{
    'name': 'PoS Order Discount Tracker',
    'version': '17.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Permite rastrear, filtrar y agrupar órdenes del PdV por el programa de lealtad o descuento aplicado.',
    'description': """
        Este módulo agrega un campo relacional (Many2many) en las órdenes del Punto de Venta
        para registrar qué programas de descuento/lealtad se aplicaron.
        Ideal para reportes y filtrado rápido (Ej: Cuenta Socios).
    """,
    'author': "OutsourceArg JuanF",
    'website': '',
    'depends':[
        'point_of_sale', 
        'loyalty'
    ],
    'data':[
        'views/pos_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}