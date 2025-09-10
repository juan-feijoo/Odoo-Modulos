import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _force_lines_recomputation_on_saved_record(self):
        _logger.info("==> Disparando recálculo de fuerza bruta para la factura: %s", self.name)
        for move in self:
            is_foreign_currency = move.currency_id != move.company_id.currency_id
            if move.state == 'draft' and is_foreign_currency and move.invoice_line_ids:
                _logger.info("==> Condiciones cumplidas. Procediendo a recalcular %s.", move.name)
                lines_data = []
                fields_to_copy = [
                    'display_type', 'sequence', 'name', 'product_id', 'product_uom_id',
                    'quantity', 'price_unit', 'discount', 'tax_ids', 'account_id',
                    'analytic_distribution',
                ]
                
                for line in move.invoice_line_ids:
                    line_values = line.read(fields_to_copy)[0]
                    
                    many2one_fields = ['product_id', 'product_uom_id', 'account_id']
                    for field in many2one_fields:
                        if line_values.get(field):
                            line_values[field] = line_values[field][0]

                    line_values['tax_ids'] = [(6, 0, line.tax_ids.ids)]
                    line_values.pop('id', None)
                    lines_data.append(line_values)

                move.write({
                    'invoice_line_ids': [
                        (5, 0, 0),
                        *[(0, 0, vals) for vals in lines_data]
                    ]
                })

    def copy(self, default=None):
        _logger.info("==> Disparador COPY detectado.")
        new_move = super().copy(default=default)
        new_move._force_lines_recomputation_on_saved_record()
        return new_move

    @api.onchange('currency_id', 'invoice_date', 'date')
    def _onchange_currency_date_trigger_recomputation(self):
        _logger.info("==> Disparador ONCHANGE detectado en factura %s.", self.name or 'NUEVA')
        if self.invoice_line_ids:
            _logger.info("==> La factura tiene líneas, forzando recálculo mediante reasignación.")
            self.invoice_line_ids = self.invoice_line_ids