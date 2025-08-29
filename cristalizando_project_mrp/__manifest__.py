# -*- coding: utf-8 -*-
{
    "name": "Project Task",
    "version": "17.0.1.0.0",
    "category": "Tools",
    "summary": "Auto-generated advanced module",
    "description": "Añade campos y lógica de negocio para la gestión de obras.",
    "author": 'Juan Feijoo',
    "depends": ["base", 'project', 'mrp'],
    "data": [
        "views/project_task_views.xml"
        "views/project_task_line_import_wizard_views.xml",
        "wizard/project_task_line_import_wizard_views.xml",
    ],
    "demo": [
        "demo/project_task_data.xml"
    ],
    "assets": {},
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True
}