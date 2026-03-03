{
    'name': 'Reporte de Ventas por Oportunidades Ganadas',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Exporta un Excel con las ventas de oportunidades ganadas filtradas por fecha',
    'description': """
        Añade un asistente (wizard) en el menú de Ventas > Reportes para generar 
        un Excel detallado de los productos vendidos provenientes de oportunidades del CRM, 
        permitiendo seleccionar un rango de fechas dinámico.
    """,
    'author': 'Outsourcearg Juan',
    'depends': ['sale_management', 'crm'],
    'data':[
        'security/ir.model.access.csv',
        'wizard/sale_report_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}