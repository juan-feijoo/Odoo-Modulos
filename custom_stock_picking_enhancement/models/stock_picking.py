# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

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
        
        customer_location = self.env.ref('stock.stock_location_customers')

        # --- LÓGICA DE ORÍGENES PARA EL REMITO PRINCIPAL ---
        all_origins = pickings.mapped('origin')
        unique_origins = sorted(list(set(o for o in all_origins if o)))
        new_picking_origin = ', '.join(unique_origins)
        if not new_picking_origin:
            new_picking_origin = ', '.join(pickings.mapped('name'))
        
        # --- CREACIÓN DEL NUEVO REMITO ---
        picking_vals = {
            'picking_type_id': outgoing_picking_type.id,
            'location_id': default_source_location.id,
            'location_dest_id': customer_location.id,
            'origin': new_picking_origin,
            'partner_id': first_picking.partner_id.id if first_picking.partner_id else False,
            'owner_id': owner_id.id if owner_id else False,
        }
        new_picking = self.env['stock.picking'].create(picking_vals)

        new_moves_data = {}
        for picking in pickings:
            for line in picking.move_line_ids:
                if line.qty_done <= 0:
                    continue
                
                product = line.product_id
                product_data = new_moves_data.get(product.id)
                
                if not product_data:
                    move = self.env['stock.move'].create({
                        'name': product.display_name, 'product_id': product.id,
                        'product_uom': line.product_uom_id.id, 'product_uom_qty': 0,
                        'location_id': default_source_location.id,
                        'location_dest_id': new_picking.location_dest_id.id,
                        'picking_id': new_picking.id,
                        'restrict_partner_id': owner_id.id if owner_id else False,
                    })
                    product_data = {'move': move, 'origins': set()}
                    new_moves_data[product.id] = product_data
                
                if picking.origin:
                    product_data['origins'].add(picking.origin)

                self.env['stock.move.line'].create({
                    'picking_id': new_picking.id,
                    'move_id': product_data['move'].id,
                    'product_id': product.id,
                    'product_uom_id': line.product_uom_id.id,
                    'qty_done': line.qty_done,
                    'location_id': default_source_location.id,
                    'location_dest_id': new_picking.location_dest_id.id,
                    'lot_id': line.lot_id.id if line.lot_id else False,
                    'owner_id': owner_id.id if owner_id else False,
                    'package_id': line.result_package_id.id if line.result_package_id else False,
                })


        for data in new_moves_data.values():
            move = data['move']
            move_origin = ', '.join(sorted(list(data['origins'])))
            total_qty = sum(l.qty_done for l in move.move_line_ids)
            move.write({
                'origin': move_origin,
                'product_uom_qty': total_qty
            })
        
        new_picking.action_confirm()
        new_picking.action_assign()
        
        return {
            'name': _('Remito Combinado'), 'type': 'ir.actions.act_window',
            'view_mode': 'form', 'res_model': 'stock.picking', 'res_id': new_picking.id,
            'target': 'current',
        }