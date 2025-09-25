from odoo import fields, models

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    temperatura = fields.Float(string="Temperatura (°C)")

    def _get_fields_stock_barcode(self):
        # Obtenemos la lista de campos del método original
        fields_list = super()._get_fields_stock_barcode()
        # Agregamos nuestro campo a la lista
        if 'temperatura' not in fields_list:
            fields_list.append('temperatura')
        return fields_list
