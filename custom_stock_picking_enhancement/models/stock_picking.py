# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_root_origin(self, picking, visited=None):
        """
        Función recursiva para encontrar el documento de origen raíz.
        """
        if visited is None:
            visited = set()
        if not picking.origin or picking.name in visited:
            return picking.origin or picking.name

        visited.add(picking.name)
        parent_picking = self.env['stock.picking'].search([('name', '=', picking.origin)], limit=1)
        
        if parent_picking:
            return self._get_root_origin(parent_picking, visited)
        else:
            return picking.origin

    def action_combine_pickings(self):
        pickings = self
        if not pickings:
            raise UserError(_("Debe seleccionar al menos un remito para combinar."))
        if any(p.state != 'done' for p in pickings):
            raise UserError(_("Solo se pueden combinar remitos que estén en estado 'Hecho'."))

        # --- VALIDACIONES ---
        owners = pickings.mapped('owner_id')
        if len(owners) > 1:
            raise UserError(_("No se pueden combinar remitos de diferentes propietarios."))
        if len(pickings.mapped('partner_id')) > 1:
            raise UserError(_("No se pueden combinar remitos de diferentes clientes."))
        
        # --- LÓGICA DE UBICACIONES Y TIPO DE OPERACIÓN ---
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
        
        default_dest_location = outgoing_picking_type.default_location_dest_id
        if not default_dest_location:
            raise UserError(_("El tipo de operación '%s' no tiene una Ubicación de Destino por Defecto configurada.", outgoing_picking_type.name))

        # --- BÚSQUEDA DE ORÍGENES RAÍZ ---
        picking_to_root_origin_map = {p.id: self._get_root_origin(p) for p in pickings}
        unique_root_origins = set(picking_to_root_origin_map.values())
        new_picking_origin = ', '.join(sorted(list(o for o in unique_root_origins if o)))
        if not new_picking_origin:
            new_picking_origin = ', '.join(pickings.mapped('name'))
        
        # --- CREACIÓN DEL NUEVO REMITO ---
        picking_vals = {
            'picking_type_id': outgoing_picking_type.id,
            'location_id': default_source_location.id,
            'location_dest_id': default_dest_location.id,
            'origin': new_picking_origin,
            'partner_id': first_picking.partner_id.id if first_picking.partner_id else False,
            'owner_id': owner_id.id if owner_id else False,
        }
        new_picking = self.env['stock.picking'].create(picking_vals)

        # --- CREACIÓN DE LÍNEAS DE MOVIMIENTO ---
        new_moves_by_product = {}
        for picking in pickings:
            root_origin_for_this_picking = picking_to_root_origin_map.get(picking.id)
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
                        'location_dest_id': new_picking.location_dest_id.id, # Correcto, hereda del nuevo picking
                        'picking_id': new_picking.id,
                        'restrict_partner_id': owner_id.id if owner_id else False,
                        'origin': root_origin_for_this_picking or picking.name,
                    })
                    new_moves_by_product[product.id] = move
                
                self.env['stock.move.line'].create({
                    'picking_id': new_picking.id, 'move_id': move.id, 'product_id': product.id,
                    'product_uom_id': line.product_uom_id.id, 'qty_done': line.qty_done,
                    'location_id': default_source_location.id, # La ubicación de donde se RECOGE el stock
                    'location_dest_id': new_picking.location_dest_id.id, # El destino final del nuevo remito
                    'lot_id': line.lot_id.id,
                    'origin': root_origin_for_this_picking or picking.name,
                    'owner_id': owner_id.id if owner_id else False,
                })

        for move in new_moves_by_product.values():
            origins = [l.origin for l in move.move_line_ids if l.origin and l.product_id == move.product_id]
            move.origin = ', '.join(sorted(list(set(origins))))
            total_qty = sum(l.qty_done for l in move.move_line_ids)
            move.write({'product_uom_qty': total_qty})
        
        return {
            'name': _('Remito Combinado (Mejorado)'), 'type': 'ir.actions.act_window',
            'view_mode': 'form', 'res_model': 'stock.picking', 'res_id': new_picking.id,
            'target': 'current',
        }