# -*- coding: utf-8 -*-
from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_grouped_services_by_section(self):
        """
        Retorna una lista de diccionarios con las líneas agrupadas por sección.
        Calcula las 6 columnas: Cantidad, Precio Unitario, % IVA, Subtotal y Total.
        Compatible con Odoo 18.
        """
        self.ensure_one()
        grouped_lines =[]
        current_section = None
        
        # Filtramos notas y recorremos ordenados por secuencia para respetar la vista del usuario
        for line in self.invoice_line_ids.filtered(lambda l: l.display_type != 'line_note').sorted('sequence'):
            
            if line.display_type == 'line_section':
                # Si ya veníamos sumando una sección previa, la guardamos
                if current_section is not None:
                    # Formateamos el set de impuestos a un texto (ej: "IVA 21%") antes de guardar
                    current_section['taxes_str'] = ", ".join(current_section['taxes'])
                    grouped_lines.append(current_section)
                
                # Iniciamos el diccionario con LAS 6 LLAVES para la nueva sección
                current_section = {
                    'name': line.name,
                    'quantity': 1.0,  # Un bloque agrupado representa 1 Unidad de servicio
                    'uom_name': 'Unidades',
                    'price_unit': 0.0,
                    'taxes': set(),   # Usamos un 'set' para que si hay varios "IVA 21%" no se duplique el texto
                    'price_subtotal': 0.0,
                    'price_total': 0.0,
                    'is_section': True
                }
            else:
                # Es una línea normal (producto o servicio)
                if current_section is not None:
                    # Acumulamos los valores en la sección
                    current_section['price_unit'] += line.price_subtotal
                    current_section['price_subtotal'] += line.price_subtotal
                    current_section['price_total'] += line.price_total
                    # Extraemos el nombre del impuesto (priorizando la descripción corta ej: "IVA 21%")
                    for tax in line.tax_ids:
                        current_section['taxes'].add(tax.description or tax.name)
                else:
                    # Es una línea suelta, le pasamos sus datos reales
                    taxes_list =[tax.description or tax.name for tax in line.tax_ids]
                    grouped_lines.append({
                        'name': line.name or line.product_id.name,
                        'quantity': line.quantity,
                        'uom_name': line.product_uom_id.name if line.product_uom_id else 'Unidades',
                        'price_unit': line.price_unit,
                        'taxes_str': ", ".join(taxes_list),
                        'price_subtotal': line.price_subtotal,
                        'price_total': line.price_total,
                        'is_section': False
                    })
                    
        # Al terminar el bucle, si quedó una sección pendiente de guardar, la agregamos
        if current_section is not None:
            current_section['taxes_str'] = ", ".join(current_section['taxes'])
            grouped_lines.append(current_section)
            
        return grouped_lines