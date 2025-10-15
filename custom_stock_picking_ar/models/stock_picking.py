# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # --- Campos de Transporte, Chofer, Aduana e Importador (Sin cambios) ---
    transport_id = fields.Many2one('res.partner', string='Transporte', domain="[('is_company', '=', True)]")
    transport_vat = fields.Char(string='CUIT Transporte', related='transport_id.vat', readonly=True)
    transport_address = fields.Char(string='Dirección Transporte', related='transport_id.contact_address_complete', readonly=True)
    driver_name = fields.Char(string='Chofer')
    driver_dni = fields.Char(string='DNI Chofer')
    vehicle_license_plate = fields.Char(string='Patente Vehículo')
    trailer_license_plate = fields.Char(string='Patente Acoplado')
    customs_broker_id = fields.Many2one('res.partner', string='Despachante Aduana')
    customs_broker_address = fields.Char(string='Dirección Despachante', related='customs_broker_id.contact_address_complete', readonly=True)
    customs_broker_vat = fields.Char(string='CUIT Despachante', related='customs_broker_id.vat', readonly=True)
    importer_id = fields.Many2one('res.partner', string='Importador')
    importer_address = fields.Char(string='Dirección Importador', related='importer_id.contact_address_complete', readonly=True)

    # --- Datos de la Factura y Venta (Campos Relacionados) ---
    sale_order_id = fields.Many2one(
        'sale.order', string='Orden de Venta',
        related='group_id.sale_id', store=True, readonly=True
    )
    commercial_invoice_id = fields.Many2one(
        'account.move', string='Factura Comercial',
        compute='_compute_commercial_invoice', store=True, readonly=True
    )

    final_destination_country = fields.Char(
        string='Mercadería Destino Final',
        related='commercial_invoice_id.x_pas_destino_del_comprobante',
        readonly=True
    )
    origin_goods_display = fields.Char(
        string='Origen Mercadería',
        compute='_compute_origin_goods_display', readonly=True
    )

    # --- Funciones Compute ---


    @api.depends('sale_order_id.invoice_ids')
    def _compute_commercial_invoice(self):

        for picking in self:
            if not picking.sale_order_id or not picking.sale_order_id.name:
                picking.commercial_invoice_id = False
                continue

            posted_invoices = picking.sale_order_id.invoice_ids.filtered(lambda inv: inv.state == 'posted')
            if posted_invoices:
                picking.commercial_invoice_id = posted_invoices[0]
                continue
            
            draft_invoices = picking.sale_order_id.invoice_ids.filtered(lambda inv: inv.state == 'draft')
            if draft_invoices:
                picking.commercial_invoice_id = draft_invoices[0]
            else:
                picking.commercial_invoice_id = False
                
    @api.depends('company_id.partner_id.state_id', 'company_id.partner_id.country_id')
    def _compute_origin_goods_display(self):
        for picking in self:
            company = picking.company_id
            if company.partner_id.state_id and company.partner_id.country_id:
                picking.origin_goods_display = f"{company.partner_id.state_id.name}, {company.partner_id.country_id.name}"
            else:
                picking.origin_goods_display = company.partner_id.country_id.name if company.partner_id.country_id else False