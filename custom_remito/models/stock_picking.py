# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError # <--- 1. IMPORTAMOS ValidationError
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    use_preprinted_remito = fields.Boolean(
        string="Usar Remito Pre-impreso",
        copy=False,
        default=False,
        help="Marcar si este albarán se imprimirá en papel pre-impreso con numeración correlativa."
    )
    nro_remito = fields.Char(
        string='Número de remito',
        copy=False,
        readonly=True,
        help="Número de secuencia para el remito pre-impreso."
    )
    name_nro_remito = fields.Char(
        string='Número de remito',
        compute='_compute_name_remito',
    )
    
    # 2. AÑADIMOS LA RESTRICCIÓN DE UNICIDAD
    @api.constrains('nro_remito', 'use_preprinted_remito', 'company_id')
    def _check_nro_remito_unique(self):
        """
        Asegura que el número de remito sea único por compañía
        solo para los albaranes marcados como pre-impresos.
        """
        for picking in self:
            # Solo validamos si la casilla está marcada y hay un número para revisar
            if not picking.use_preprinted_remito or not picking.nro_remito:
                continue

            # Buscamos otros albaranes (excluyendo el actual) que usen el mismo número
            domain = [
                ('company_id', '=', picking.company_id.id),
                ('use_preprinted_remito', '=', True),
                ('nro_remito', '=', picking.nro_remito),
                ('id', '!=', picking.id)
            ]
            
            if self.env['stock.picking'].search(domain, limit=1):
                raise ValidationError(
                    _("¡Número Duplicado! El número de remito '%s' ya ha sido utilizado en otro albarán.") % picking.nro_remito
                )


    @api.depends('nro_remito')
    def _compute_name_remito(self):
        for record in self:
            record.name_nro_remito = record.nro_remito

    def button_validate(self):
        for picking in self:
            if picking.use_preprinted_remito and picking.picking_type_code == 'outgoing':
                if not picking.nro_remito:
                    sequence_code = 'stock.picking.remito'
                    picking.nro_remito = self.env['ir.sequence'].with_company(picking.company_id).next_by_code(sequence_code)
                
                if not picking.nro_remito:
                    raise UserError(_("No se pudo generar el número de remito. Verifique que la secuencia '%s' exista y esté configurada para la compañía '%s'.") % (sequence_code, picking.company_id.name))

        # La validación @api.constrains se ejecutará automáticamente antes de que la transacción se confirme.
        return super(StockPicking, self).button_validate()

    def change_number(self, new_number):
        self.ensure_one()
        try:
            num = int(new_number)
        except ValueError:
            raise UserError(_("El número de remito debe ser un valor numérico para la secuencia."))
        
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'stock.picking.remito'),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

        if sequence:
            prefix = sequence.prefix or ''
            padding = sequence.padding
            formatted_number = f"{prefix}{new_number.zfill(padding)}"
            
            # Al hacer este .write(), la validación @api.constrains se disparará automáticamente.
            self.write({'nro_remito': formatted_number})
            
            sequence.sudo().write({
                'number_next_actual': num + 1
            })
        else:
            raise UserError(_("No se encontró una secuencia con el código 'stock.picking.remito' para la compañía actual."))

    def action_open_update_sequence_wizard(self):
        self.ensure_one()
        current_number_only = ''.join(filter(str.isdigit, self.nro_remito or '0'))
        
        return {
            'name': _('Actualizar Número de Remito'),
            'type': 'ir.actions.act_window',
            'res_model': 'update.remito.sequence.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_current_number': current_number_only,
                'default_main_wizard_id': self.id,
            }
        }

# El Wizard no necesita cambios. La validación está en el modelo principal.
class UpdateRemitoequenceWizard(models.TransientModel):
    _name = 'update.remito.sequence.wizard'
    _description = 'Wizard para actualizar número de secuencia de remitos'
    
    current_number = fields.Char(string='Número Actual', readonly=True)
    new_number = fields.Char(string='Nuevo Número', required=True)
    main_wizard_id = fields.Many2one('stock.picking', string='Wizard Principal')
    
    def action_confirm(self):
        self.ensure_one()
        if not self.main_wizard_id:
            raise UserError(_("No se encontró el remito a modificar"))
        if not self.new_number.isdigit():
            raise UserError(_("El nuevo número debe ser un valor numérico."))
        if self.new_number == self.current_number:
            raise UserError(_("El nuevo número debe ser diferente al actual"))
        
        self.main_wizard_id.change_number(self.new_number)
        return {'type': 'ir.actions.act_window_close'}