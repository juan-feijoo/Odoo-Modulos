from odoo import models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_imputed_moves_data(self):
        """
        Devuelve las facturas y Notas de Crédito imputadas.
        Soporta Recordsets múltiples (Payment Bundles).
        """
        res = []
        invoices = self.env['account.move']
        all_payment_partials = self.env['account.partial.reconcile']
        
        # 1. Iteramos sobre TODOS los pagos del recordset (sin self.ensure_one)
        for payment in self:
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
                        
                        # Agrupamos si varios pagos (ej. retenciones + banco) imputan a la misma factura
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

        # 2. Buscar Notas de Crédito conciliadas a esas facturas específicas
        for inv in invoices.filtered(lambda m: m.move_type in ('out_invoice', 'in_invoice')):
            inv_lines = inv.line_ids.filtered(
                lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable')
            )
            for line in inv_lines:
                partials = line.matched_debit_ids | line.matched_credit_ids
                # Excluir las conciliaciones que provienen de los pagos del recibo actual
                partials = partials - all_payment_partials 
                
                for partial in partials:
                    counterpart_line = partial.debit_move_id if partial.credit_move_id == line else partial.credit_move_id
                    nc_move = counterpart_line.move_id
                    
                    if nc_move.move_type in ('out_refund', 'in_refund'):
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
                            # Si la NC compensa múltiples facturas en este mismo recibo
                            existing_nc['amount_imputed'] += partial.amount * -1

                        # Ajustamos el monto imputado de la factura original para sumar la compensación de la NC
                        inv_res = next((r for r in res if r['move_id'] == inv.id), None)
                        if inv_res:
                            inv_res['amount_imputed'] += partial.amount

        return res