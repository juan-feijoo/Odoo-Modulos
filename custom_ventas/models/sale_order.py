# -*- coding: utf-8 -*-
from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()

        pricelist_name = self.pricelist_id.name
        if pricelist_name == 'Transferencias':
            payment_term = self.env.ref('account.account_payment_term_immediate', raise_if_not_found=False)
            journal = self.env['account.journal'].search([('name', '=', '00004 - Facturación Electrónica Odoo')], limit=1)
            
            if payment_term:
                invoice_vals['invoice_payment_term_id'] = payment_term.id
            if journal:
                invoice_vals['journal_id'] = journal.id

        elif pricelist_name == 'Efectivo':
            payment_term = self.env.ref('account.account_payment_term_immediate', raise_if_not_found=False)
            journal = self.env['account.journal'].search([('name', '=', 'Comprobantes')], limit=1)

            if payment_term:
                invoice_vals['invoice_payment_term_id'] = payment_term.id
            if journal:
                invoice_vals['journal_id'] = journal.id
        
        return invoice_vals