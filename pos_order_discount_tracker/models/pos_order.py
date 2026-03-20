from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    applied_program_ids = fields.Many2many(
        comodel_name='loyalty.program',
        relation='pos_order_loyalty_program_rel',
        column1='pos_order_id',
        column2='loyalty_program_id',
        string='Descuentos Aplicados',
        compute='_compute_applied_program_ids',
        store=True,
        help="Programas de lealtad o descuentos que se aplicaron en esta orden."
    )

    @api.depends('lines.reward_id.program_id')
    def _compute_applied_program_ids(self):
        for order in self:
            # Extrae todos los programas de lealtad/descuento de las líneas de la orden
            programs = order.lines.mapped('reward_id.program_id')
            if programs:
                # El comando (6, 0, [IDs]) reemplaza los registros vinculados por los nuevos
                order.applied_program_ids = [(6, 0, programs.ids)]
            else:
                # Si no hay programas (se eliminó la línea de descuento), vaciamos el campo
                order.applied_program_ids = False