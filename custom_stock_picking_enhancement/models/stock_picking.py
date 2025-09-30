# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_combine_pickings(self):
        pickings = self
        if any(p.state != 'done' for p in pickings):
            raise UserError(_("Solo se pueden combinar remitos que estén en estado 'Hecho'."))

        # --- VALIDACIONES ---
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

        # --- LÓGICA DE ORÍGENES  ---
        all_origins = pickings.mapped('origin')
        unique_origins = sorted(list(set(o for o in all_origins if o)))
        new_picking_origin = ', '.join(unique_origins) or ', '.join(pickings.mapped('name'))
        
        # --- CREACIÓN DEL NUEVO REMITO  ---
        picking_vals = {
            'picking_type_id': outgoing_picking_type.id,
            'location_id': default_source_location.id,
            'location_dest_id': customer_location.id,
            'origin': new_picking_origin,
            'partner_id': first_picking.partner_id.id if first_picking.partner_id else False,
            'owner_id': owner_id.id if owner_id else False,
        }
        new_picking = self.env['stock.picking'].create(picking_vals)

        product_data_map = {}
        for picking in pickings:
            for line in picking.move_line_ids.filtered(lambda l: l.qty_done > 0):
                product = line.product_id
                
                # Inicializar el diccionario para este producto si es la primera vez que lo vemos
                product_data_map.setdefault(product, {
                    'total_quantity': 0.0,
                    'origins': set(),
                    'lines_details': [],
                    'uom_id': line.product_uom_id
                })
                
                # Acumular la cantidad total
                product_data_map[product]['total_quantity'] += line.qty_done
                
                # Agregar el origen
                if picking.origin:
                    product_data_map[product]['origins'].add(picking.origin)
                
                product_data_map[product]['lines_details'].append({
                    'quantity': line.qty_done,
                    'lot_id': line.lot_id,
                    'package_id': line.result_package_id,
                })
        
        for product, data in product_data_map.items():
            move_origin = ', '.join(sorted(list(data['origins'])))
            move = self.env['stock.move'].create({
                'name': product.display_name,
                'product_id': product.id,
                'product_uom': data['uom_id'].id,
                'product_uom_qty': data['total_quantity'], # <-- ¡CLAVE! Se crea con la cantidad total
                'location_id': default_source_location.id,
                'location_dest_id': new_picking.location_dest_id.id,
                'picking_id': new_picking.id,
                'origin': move_origin,
                'restrict_partner_id': owner_id.id if owner_id else False,
            })

            for line_detail in data['lines_details']:
                self.env['stock.move.line'].create({
                    'picking_id': new_picking.id,
                    'move_id': move.id,
                    'product_id': product.id,
                    'product_uom_id': data['uom_id'].id,
                    'quantity': line_detail['quantity'],
                    'qty_done': 0,
                    'location_id': default_source_location.id,
                    'location_dest_id': new_picking.location_dest_id.id,
                    'lot_id': line_detail['lot_id'].id if line_detail['lot_id'] else False,
                    'owner_id': owner_id.id if owner_id else False,
                    'package_id': line_detail['package_id'].id if line_detail['package_id'] else False,
                })

        #Lineas comentadas para dejar en borrador
        #new_picking.action_confirm()
        #new_picking.action_assign()
        
        return {
            'name': _('Remito Combinado'), 'type': 'ir.actions.act_window',
            'view_mode': 'form', 'res_model': 'stock.picking', 'res_id': new_picking.id,
            'target': 'current',
        }