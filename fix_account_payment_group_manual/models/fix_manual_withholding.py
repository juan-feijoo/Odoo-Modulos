# -*- coding: utf-8 -*-
from odoo import models, api, Command, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class L10nArPaymentWithholding(models.Model):
    _inherit = 'l10n_ar.payment.withholding'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Obtenemos el grupo de pago si existe
            payment_group = False
            if vals.get('multiple_payment_id'):
                payment_group = self.env['account.payment.multiplemethods'].browse(vals['multiple_payment_id'])
            
            if not vals.get('currency_id'):
                if payment_group:
                    vals['currency_id'] = payment_group.company_currency_id.id or payment_group.company_id.currency_id.id
                if not vals.get('currency_id'):
                    vals['currency_id'] = self.env.company.currency_id.id
            
            if not vals.get('company_id'):
                if payment_group:
                    vals['company_id'] = payment_group.company_id.id
                else:
                    vals['company_id'] = self.env.company.id

        return super(L10nArPaymentWithholding, self).create(vals_list)

class AccountPaymentMultipleMethods(models.Model):
    _inherit = 'account.payment.multiplemethods'

    def action_reconcile_payments(self):
        self.ensure_one()
        _logger.info(f"=== INICIO FIX MULTI-COMPANY: action_reconcile_payments (Grupo: {self.name}) ===")
        
        payments = self.to_pay_payment_ids.filtered(lambda p: p.state == 'draft')
        
        if not payments:
             if not self.is_advanced_payment and not self.to_pay_payment_ids:
                 raise UserError("No hay pagos cargados para procesar.")
      
        current_company_id = self.company_id.id

        for w_line in self.withholding_line_ids:
            if not w_line.currency_id:
                w_line.currency_id = self.company_currency_id.id or self.env.company.currency_id.id

            if w_line.company_id.id != current_company_id:
                _logger.info(f"FIX: Corrigiendo compañía en retención {w_line.id}. De {w_line.company_id.name} a {self.company_id.name}")
                w_line.company_id = current_company_id

            if w_line.tax_id.company_id and w_line.tax_id.company_id.id != current_company_id:
                raise ValidationError(
                    f"Error de Configuración Multi-Compañía:\n"
                    f"La retención '{w_line.tax_id.name}' pertenece a la empresa '{w_line.tax_id.company_id.name}', "
                    f"pero estás intentando pagar desde '{self.company_id.name}'.\n\n"
                    f"Por favor, elimina la línea de retención y selecciona un impuesto que pertenezca a {self.company_id.name}."
                )

        if self.withholding_line_ids and payments:
            target_payment = payments[0] 
            _logger.info(f"FIX: Vinculando retenciones al pago {target_payment.id}")
            
            try:
                self.withholding_line_ids.write({
                    'payment_id': target_payment.id,
                    'company_id': current_company_id # Refuerzo extra
                })
                
                target_payment.write({
                    'l10n_ar_withholding_line_ids': [Command.set(self.withholding_line_ids.ids)]
                })
                target_payment.flush_recordset()
                
            except Exception as e:
                _logger.error(f"FIX ERROR: Falló vinculación: {str(e)}")

        if self.is_advanced_payment:
            _logger.info("Modo: Pago Adelantado")
            for payment in payments:
                payment.action_post()
        else:
            _logger.info("Modo: Pago de Deuda")
            invoices = self.to_pay_move_line_ids.filtered(lambda line: not line.reconciled).sorted(key=lambda line: line.date)
            
            if not invoices and not payments:
                 raise UserError("No hay facturas o pagos pendientes.")

            for payment in payments:
                remaining_amount = payment.amount
                
                for invoice_line in invoices:
                    invoice_balance = invoice_line.amount_residual
                    amount_to_reconcile = 0
                    
                    if payment.partner_type == 'customer' and payment.payment_type == 'inbound':
                        if invoice_balance > 0:
                            amount_to_reconcile = min(remaining_amount, invoice_balance)
                            if amount_to_reconcile > 0:
                                payment.write({'to_pay_move_line_ids': [(4, invoice_line.id)]})
                                remaining_amount -= amount_to_reconcile

                    elif payment.partner_type == 'supplier' and payment.payment_type == 'outbound':
                        if invoice_balance < 0:
                            amount_to_reconcile = min(remaining_amount, abs(invoice_balance))
                            if amount_to_reconcile > 0:
                                payment.write({'to_pay_move_line_ids': [(4, invoice_line.id)]})
                                remaining_amount -= amount_to_reconcile
    
                    if remaining_amount <= 0:
                        break
                
                if payment.state == 'draft':
                    payment.action_post()

        # Secuencias
        if not self.name:
            if self.payment_type == 'inbound':
                self.name = self.env['ir.sequence'].next_by_code('x_recibo_de_pagos') or 'New'
            else:
                self.name = self.env['ir.sequence'].next_by_code('x_reporte_de_pagos') or 'New'
            self.sequence_used = self.name
            
        self.state = 'posted'
        return