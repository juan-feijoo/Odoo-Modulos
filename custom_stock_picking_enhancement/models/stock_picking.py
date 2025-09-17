# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_combine_pickings(self):
        _logger.info("==== EJECUTANDO CÓDIGO del módulo 'custom_stock_picking_enhancement' ====")
        pickings = self

        if not pickings:
            raise UserError(_("Debe seleccionar al menos un remito para combinar."))
        if any(p.state != 'done' for p in pickings):
            raise UserError(_("Solo se pueden combinar remitos que estén en estado 'Hecho'."))

        owners = pickings.mapped('owner_id')
        if len(owners) > 1:
            raise UserError(_("No se pueden combinar remitos de diferentes propietarios."))
        
        if len(pickings.mapped('partner_id')) > 1:
            raise UserError(_("No se pueden combinar remitos de diferentes clientes."))
        if len(pickings.mapped('location_dest_id')) > 1:
            raise UserError(_("Los remitos deben tener la misma Ubicación de Destino."))

        first_picking = pickings[0]
        owner_id = first_picking.owner_id
        warehouse = first_picking.picking_type_id.warehouse_id
        if not warehouse:
            raise UserError(_("No se pudo determinar un almacén para las operaciones."))
        
        outgoing_picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'), ('warehouse_id', '=', warehouse.id)
        ], limit=1)
        if not outgoing_picking_type:
            raise UserError(_("No se encontró un tipo de operación de 'Entrega' para el almacén %s.", warehouse.name))

        default_source_location = outgoing_picking_type.default_location_src_id
        if not default_source_location:
            raise UserError(_("El tipo de operación '%s' no tiene una Ubicación de Origen por Defecto configurada.", outgoing_picking_type.name))

        new_picking_origin = ', '.join(pickings.mapped('name'))
        
        picking_vals = {
            'picking_type_id': outgoing_picking_type.id,
            'location_id': default_source_location.id,
            'location_dest_id': first_picking.location_dest_id.id,
            'origin': new_picking_origin,
            'partner_id': first_picking.partner_id.id if first_picking.partner_id else False,
            'owner_id': owner_id.id if owner_id else False,
        }
        new_picking = self.env['stock.picking'].create(picking_vals)
        _logger.info(f"Remito combinado {new_picking.name} creado. Estado inicial: {new_picking.state}")

        new_moves_by_product = {}
        for picking in pickings:
            for line in picking.move_line_ids:
                if line.qty_done <= 0:
                    continue
                
                product = line.product_id
                move = new_moves_by_product.get(product.id)
                if not move:
                    move = self.env['stock.move'].create({
                        'name': product.display_name, 'product_id': product.id,
                        'product_uom': line.product_uom_id.id, 'product_uom_qty': 0,
                        'location_id': default_source_location.id,
                        'location_dest_id': new_picking.location_dest_id.id,
                        'picking_id': new_picking.id,
                        'restrict_partner_id': owner_id.id if owner_id else False,
                        'origin': picking.name,
                    })
                    new_moves_by_product[product.id] = move
                
                self.env['stock.move.line'].create({
                    'picking_id': new_picking.id, 'move_id': move.id, 'product_id': product.id,
                    'product_uom_id': line.product_uom_id.id, 'qty_done': line.qty_done,
                    'location_id': line.location_id.id,
                    'location_dest_id': new_picking.location_dest_id.id,
                    'lot_id': line.lot_id.id, 
                    'x_origin_document': picking.name,
                    'owner_id': owner_id.id if owner_id else False,
                })

        for move in new_moves_by_product.values():
            # Actualizamos el origin del movimiento para que contenga todos los remitos de ese producto.
            origins = [
                l.x_origin_document 
                for l in move.move_line_ids 
                if l.x_origin_document and l.product_id == move.product_id
            ]
            move.origin = ', '.join(sorted(list(set(origins))))

            # Actualizamos la cantidad total
            total_qty = sum(l.qty_done for l in move.move_line_ids)
            move.write({'product_uom_qty': total_qty})
        
        _logger.info(f"Estado final del remito ANTES de retornar: {new_picking.state}")

        return {
            'name': _('Remito Combinado'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'res_id': new_picking.id,
            'target': 'current',
        }

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    x_origin_document = fields.Char(string="Documento Origen", readonly=True, copy=False)