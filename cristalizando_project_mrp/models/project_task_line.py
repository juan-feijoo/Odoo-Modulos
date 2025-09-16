from odoo import models, fields

class ProjectTaskLine(models.Model):
    _name = 'project.task.line'
    _description = 'Línea de Insumo para Tarea de Proyecto'

    # Campos base
    task_id = fields.Many2one('project.task', string='Tarea', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Insumo', required=True)
    quantity = fields.Float(string='Cantidad', default=1.0)
    price_unit = fields.Float('Precio Unitario', digits='Product Price', default=0.0)
    
    # Unidad de Medida (la mantenemos para consistencia)
    uom_id = fields.Many2one('uom.uom', string='Unidad de Medida', related='product_id.uom_id', readonly=True)

    x_studio_descripcion = fields.Text(string='Descripción')
    x_studio_tipologia = fields.Char(string='Tipología')
    x_studio_precio_unitario_carpinteria = fields.Float(string='Precio Unitario Carpintería')
    x_studio_codigo_distancia_km = fields.Char(string='Código Distancia/KM')
    x_studio_precio_unitario_instalacion = fields.Float(string='Precio Unitario Instalación')
    codigo = fields.Char(string='Código (Excel)')
    subtotal_unidad = fields.Float(string='Subtotal Unidad (Excel)')
    subtotal = fields.Float(string='Subtotal (Excel)')
    nombre_producto = fields.Char(string='Nombre del Producto (Excel)')