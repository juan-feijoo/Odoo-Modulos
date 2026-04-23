# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Proveedor de Pago: Macro Clic",
    'version': '18.0.1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 360,
    'summary': "Pasarela de pagos Macro Clic (ASJ Servicios) para Argentina.",
    'depends': ['payment'],
    'data':[
        'views/payment_macro_clic_templates.xml',
        'views/payment_provider_views.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
    ],
    'neutralize_sql': ['data/neutralize.sql'],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}