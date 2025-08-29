# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import ValidationError

class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    def unpack(self):
        """ Valida el estado del paquete antes de desempaquetar. """
        for package in self:
            if not package.quant_ids:
                raise ValidationError(
                    _("Operación Bloqueada: El paquete '%(package_name)s' está vacío.") % 
                    {'package_name': package.name}
                )

            if any(quant.quantity < 0 for quant in package.quant_ids):
                raise ValidationError(
                    _("Operación Bloqueada: El paquete '%(package_name)s' contiene stock negativo.") % 
                    {'package_name': package.name}
                )
        
        return super(StockQuantPackage, self).unpack()