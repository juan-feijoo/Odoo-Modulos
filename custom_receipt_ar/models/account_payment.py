from odoo import models
import logging

# Iniciamos el logger
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_imputed_moves_data(self):
        # LOG INICIAL: Vemos exactamente qué IDs de pagos están llegando
        _logger.info("========== INICIANDO _get_imputed_moves_data (CUSTOM NC) ==========")
        _logger.info(f"Pagos recibidos en el Recordset: {self.ids}")
        
        res = []
        invoices = self.env['account.move']
        all_payment_partials = self.env['account.partial.reconcile']
        
        # Iteramos sobre los pagos (Soporta múltiples pagos del Payment Bundle)
        for payment in self:
            _logger.info(f"Procesando liquidez del Pago ID: {payment.id}")
            liquidity_lines = payment.move_id.line_ids.filtered(
                lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable')
            )

            for line in liquidity_lines:
                partials = line.matched_debit_ids | line.matched_credit_ids
                all_payment_partials |= partials
                
                for partial in partials:
                    counterpart_line = partial.debit_move_id if partial.credit_move_id == line else partial.credit_move_id
                    move = counterpart_line.move_id
                    
                    sign = -1 if move.move_type in ('out_refund', 'in_refund') else 1
                    
                    if move.move_type in ('out_invoice', 'in_invoice', 'out_refund', 'in_refund'):
                        invoices |= move
                        
                        existing = next((r for r in res if r['move_id'] == move.id), None)
                        if existing:
                            existing['amount_imputed'] += partial.amount * sign
                        else:
                            res.append({
                                'move_id': move.id,
                                'move_name': move.name,
                                'date_due': move.invoice_date_due or move.date,
                                'amount_original': move.amount_total * sign,
                                'amount_imputed': partial.amount * sign,
                                'currency': move.currency_id,
                            })

        _logger.info(f"Facturas directamente afectadas por el recibo: {invoices.mapped('name')}")

        # Buscar Notas de Crédito
        for inv in invoices.filtered(lambda m: m.move_type in ('out_invoice', 'in_invoice')):
            inv_lines = inv.line_ids.filtered(
                lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable')
            )
            for line in inv_lines:
                partials = line.matched_debit_ids | line.matched_credit_ids
                partials = partials - all_payment_partials 
                
                for partial in partials:
                    counterpart_line = partial.debit_move_id if partial.credit_move_id == line else partial.credit_move_id
                    nc_move = counterpart_line.move_id
                    
                    if nc_move.move_type in ('out_refund', 'in_refund'):
                        _logger.info(f"¡Nota de Crédito encontrada! NC: {nc_move.name} compensando Factura: {inv.name}")
                        existing_nc = next((r for r in res if r['move_id'] == nc_move.id), None)
                        
                        if not existing_nc:
                            res.append({
                                'move_id': nc_move.id,
                                'move_name': nc_move.name,
                                'date_due': nc_move.invoice_date_due or nc_move.date,
                                'amount_original': nc_move.amount_total * -1,
                                'amount_imputed': partial.amount * -1,
                                'currency': nc_move.currency_id,
                            })
                        else:
                            existing_nc['amount_imputed'] += partial.amount * -1

                        inv_res = next((r for r in res if r['move_id'] == inv.id), None)
                        if inv_res:
                            inv_res['amount_imputed'] += partial.amount

        _logger.info(f"========== FIN _get_imputed_moves_data. Total líneas a renderizar: {len(res)} ==========")
        return res