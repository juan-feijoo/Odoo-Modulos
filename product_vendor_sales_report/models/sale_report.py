# -*- coding: utf-8 -*-
from odoo import models, fields
import re

class SaleReport(models.Model):
    _inherit = 'sale.report'

    main_vendor_id = fields.Many2one('res.partner', string='Proveedor Principal', readonly=True)

    # =======================================================
    # 1. INYECCIÓN EN LA CONSULTA DE PEDIDOS DE VENTA (sale)
    # =======================================================
    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['main_vendor_id'] = "t.main_vendor_id"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += ", t.main_vendor_id"
        return res

    # =======================================================
    # 2. INYECCIÓN EN LA CONSULTA DE PUNTO DE VENTA (pos_sale)
    # =======================================================
    def _select_pos(self, *args, **kwargs):
        res = super()._select_pos(*args, **kwargs)
        # Odoo (pos_sale) inyecta automáticamente 'NULL AS main_vendor_id' en su string.
        # Usamos regex para reemplazar de manera segura ese NULL por el valor real de la tabla.
        res = re.sub(
            r'NULL\s+AS\s+main_vendor_id', 
            't.main_vendor_id AS main_vendor_id', 
            res, 
            flags=re.IGNORECASE
        )
        return res

    def _group_by_pos(self):
        res = super()._group_by_pos()
        # En el GROUP BY no hay inyección automática, por lo que aquí sí concatenamos normalmente.
        res += ", t.main_vendor_id"
        return res