# -*- coding: utf-8 -*-
from odoo import fields, models

class SaleReport(models.Model):
    _inherit = "sale.report"

    # 1. Agregamos un nuevo campo calculado.
    invoice_status_computed = fields.Char(
        string="Estado de la Factura", # Usamos la misma etiqueta para reemplazar el original
        compute='_compute_invoice_status_computed',
        help="Campo calculado para mostrar el estado de factura de órdenes de PDV."
    )
    
    def _compute_invoice_status_computed(self):
        pos_order_lines = self.filtered(lambda r: r.order_reference and r.order_reference._name == 'pos.order')
        
        for line in (self - pos_order_lines):
            # Mapeamos los valores estándar a sus etiquetas en español para consistencia.
            if line.invoice_status == 'invoiced':
                line.invoice_status_computed = 'Totalmente Facturado'
            elif line.invoice_status == 'to invoice':
                line.invoice_status_computed = 'Por Facturar'
            elif line.invoice_status == 'no':
                line.invoice_status_computed = 'Nada que facturar'
            else:
                line.invoice_status_computed = '' # Valor por defecto

        # Procesamos las líneas de PDV
        if pos_order_lines:
            for line in pos_order_lines:
                pos_order = line.order_reference
                if pos_order.state == 'invoiced':
                    line.invoice_status_computed = 'Totalmente Facturado'
                else:
                    line.invoice_status_computed = 'Nada que facturar'