# -*- coding: utf-8 -*-
from odoo import models, _, api
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from collections import defaultdict

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        """ Valida que haya stock suficiente en el paquete al validar un traslado. """
        demanded_quantities = defaultdict(float)

        for line in self.move_line_ids:
            if line.qty_done > 0 and line.package_id and line.location_id.usage == 'internal':
                key = (line.package_id, line.product_id)
                demanded_quantities[key] += line.qty_done

        if demanded_quantities:
            for (package, product), demanded_qty in demanded_quantities.items():
                available_qty = self.env['stock.quant']._get_available_quantity(
                    product, package.location_id, package_id=package, strict=True
                )

                if float_compare(demanded_qty, available_qty, precision_rounding=product.uom_id.rounding) > 0:
                    raise ValidationError(
                        _("Validación Fallida: No hay suficiente stock para el producto '%(product_name)s' en el paquete '%(package_name)s'.\n\n"
                          "Cantidad Requerida: %(demanded_qty)s\n"
                          "Cantidad Disponible: %(available_qty)s") % {
                              'product_name': product.display_name,
                              'package_name': package.name,
                              'demanded_qty': demanded_qty,
                              'available_qty': available_qty,
                          }
                    )
        
        return super(StockPicking, self).button_validate()