# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    main_vendor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor Principal',
        compute='_compute_main_vendor',
        store=True,
        index=True,
    )

    @api.depends('seller_ids', 'seller_ids.sequence')
    def _compute_main_vendor(self):
        for product in self:
            if product.seller_ids:
                # Odoo prioriza por el campo 'sequence' internamente
                product.main_vendor_id = product.seller_ids[0].partner_id
            else:
                product.main_vendor_id = False