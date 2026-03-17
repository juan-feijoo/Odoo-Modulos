# -*- coding: utf-8 -*-
from odoo import models, fields

class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    main_vendor_id = fields.Many2one('res.partner', string='Proveedor Principal', readonly=True)

    def _select(self):
        # En el reporte del POS, la tabla product.template tiene el alias 'pt'
        return super()._select() + ", pt.main_vendor_id AS main_vendor_id"

    def _group_by(self):
        return super()._group_by() + ", pt.main_vendor_id"