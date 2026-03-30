# -*- coding: utf-8 -*-
from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_grouped_services_by_section(self):
        """
        Retorna una lista de diccionarios con las líneas de la COTIZACIÓN agrupadas por sección.
        Calcula las 6 columnas: Cantidad, Precio Unitario, % IVA, Subtotal y Total.
        """
        self.ensure_one()
        grouped_lines =[]
        current_section = None
        
        # En ventas iteramos sobre 'order_line'
        for line in self.order_line.filtered(lambda l: l.display_type != 'line_note').sorted('sequence'):
            
            if line.display_type == 'line_section':
                if current_section is not None:
                    current_section['taxes_str'] = ", ".join(current_section['taxes'])
                    grouped_lines.append(current_section)
                
                current_section = {
                    'name': line.name,
                    'quantity': 1.0, 
                    'uom_name': 'Unidades',
                    'price_unit': 0.0,
                    'taxes': set(), 
                    'price_subtotal': 0.0,
                    'price_total': 0.0,
                    'is_section': True
                }
            else:
                if current_section is not None:
                    current_section['price_unit'] += line.price_subtotal
                    current_section['price_subtotal'] += line.price_subtotal
                    current_section['price_total'] += line.price_total
                    # En ventas el campo de impuestos es 'tax_id'
                    for tax in line.tax_id:
                        current_section['taxes'].add(tax.description or tax.name)
                else:
                    taxes_list = [tax.description or tax.name for tax in line.tax_id]
                    grouped_lines.append({
                        'name': line.name or line.product_template_id.name or line.product_id.name,
                        'quantity': line.product_uom_qty, # En ventas es product_uom_qty
                        'uom_name': line.product_uom.name if line.product_uom else 'Unidades',
                        'price_unit': line.price_unit,
                        'taxes_str': ", ".join(taxes_list),
                        'price_subtotal': line.price_subtotal,
                        'price_total': line.price_total,
                        'is_section': False
                    })
                    
        if current_section is not None:
            current_section['taxes_str'] = ", ".join(current_section['taxes'])
            grouped_lines.append(current_section)
            
        return grouped_lines