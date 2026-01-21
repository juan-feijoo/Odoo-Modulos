# -*- coding: utf-8 -*-
from odoo import models, fields, api

class L10nArPaymentWithholding(models.Model):
    _inherit = "l10n_ar.payment.withholding"

    accumulated_base_amount = fields.Monetary(
        string="Base Imponible Acumulada",
        compute="_compute_accumulated_base_amount",
        currency_field='currency_id',
        help="Suma de la base del pago actual más las bases de pagos anteriores en el mismo periodo (solo Ganancias)."
    )

    @api.depends('base_amount', 'tax_id', 'payment_id.date', 'payment_id.partner_id', 'payment_id.state', 'payment_id.move_id')
    def _compute_accumulated_base_amount(self):
        for rec in self:
            # 1. Por defecto, el acumulado es la base actual
            current_base = rec.base_amount
            rec.accumulated_base_amount = current_base

            # 2. Verificamos si es impuesto a las Ganancias
            tax = rec._get_withholding_tax()
            if not tax or tax.l10n_ar_tax_type not in ['earnings', 'earnings_scale']:
                continue

            # 3. Obtenemos el dominio estándar que busca los pagos del periodo
            # Este método ya viene en el módulo original
            domain = rec._get_same_period_base_domain()

            if rec.payment_id.move_id:
                domain.append(('move_id', '!=', rec.payment_id.move_id.id))

            other_payments_base = 0.0
            
            # Ejecutamos la consulta con el dominio modificado
            result = rec.env["account.move.line"]._read_group(
                domain, ["partner_id"], ["balance:sum"]
            )
            
            if result:
                other_payments_base = abs(result[0][1])

            rec.accumulated_base_amount = other_payments_base + current_base