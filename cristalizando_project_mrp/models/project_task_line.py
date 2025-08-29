# -*- coding: utf-8 -*-
from odoo import models, fields

class ProjectTaskInsumoLine(models.Model):
    _name = 'project.task.line'
    _description = 'Línea de Insumo para Tarea de Proyecto'

    task_id = fields.Many2one('project.task', string='Tarea', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Insumo', required=True)
    quantity = fields.Float(string='Cantidad', default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unidad de Medida', related='product_id.uom_id', readonly=True)

    # Campos adicionales para importar desde Excel
    tipologia = fields.Char(string='Tipología')
    codigo = fields.Char(string='Código')
    descripcion = fields.Char(string='Descripción')
    precio_unitario_carpinteria = fields.Float(string='Precio Unitario Carpintería')
    codigo_distancia_km = fields.Char(string='Código Distancia /KM')
    precio_unitario_instalacion = fields.Float(string='Precio Unitario Instalación')
    subtotal_unidad = fields.Float(string='Subtotal Unidad')
    subtotal = fields.Float(string='Subtotal')
    nombre_producto = fields.Char(string='Nombre del Producto')