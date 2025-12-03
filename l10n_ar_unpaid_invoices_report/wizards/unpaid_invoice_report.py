from odoo import models, fields, api, _
from odoo.exceptions import UserError
import io
import xlsxwriter
import base64

class UnpaidInvoiceReportWizard(models.TransientModel):
    _name = 'unpaid.invoice.report.wizard'
    _description = 'Reporte de Facturas Impagas con Detalle'

    date_from = fields.Date(string='Fecha Desde', required=True)
    date_to = fields.Date(string='Fecha Hasta', required=True)
    
    # Campo binario para descargar el archivo
    excel_file = fields.Binary('Reporte Excel', readonly=True)
    file_name = fields.Char('Nombre del Archivo', readonly=True)

    def action_generate_excel(self):
        # 1. Definir el buffer de memoria
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Facturas Impagas')

        # 2. Estilos
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        money_format = workbook.add_format({'num_format': '$ #,##0.00', 'border': 1})
        text_format = workbook.add_format({'border': 1})

        # 3. Encabezados
        headers = [
            'Cliente', 'CUIT/DNI', 'Factura', 'Fecha Factura', 
            'Fecha Vencimiento', 'Producto', 'Cantidad', 
            'Precio Unit.', 'Subtotal', 'Saldo Pendiente Factura'
        ]
        
        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_format)
            sheet.set_column(col, col, 15) # Ancho de columna

        # 4. Búsqueda de datos (ORM)
        # Buscamos líneas de factura (account.move.line)
        domain = [
            ('move_id.move_type', '=', 'out_invoice'), # Solo facturas de cliente
            ('move_id.state', '=', 'posted'),          # Solo publicadas
            ('move_id.payment_state', '!=', 'paid'),   # No pagadas (incluye parciales)
            ('display_type', '=', 'product'),          # Solo líneas de producto
            ('move_id.invoice_date', '>=', self.date_from),
            ('move_id.invoice_date', '<=', self.date_to),
        ]
        
        # En Argentina es importante el orden cronológico
        lines = self.env['account.move.line'].search(domain, order='date asc, move_name asc')

        row = 1
        for line in lines:
            move = line.move_id
            
            # Datos del Cliente y Factura
            sheet.write(row, 0, move.partner_id.name, text_format)
            sheet.write(row, 1, move.partner_id.vat or '', text_format)
            sheet.write(row, 2, move.name, text_format) # En AR suele ser el formato 0001-00001234
            sheet.write(row, 3, move.invoice_date, date_format)
            sheet.write(row, 4, move.invoice_date_due, date_format)
            
            # Datos del Producto
            sheet.write(row, 5, line.product_id.name or line.name, text_format)
            sheet.write(row, 6, line.quantity, text_format)
            sheet.write(row, 7, line.price_unit, money_format)
            sheet.write(row, 8, line.price_subtotal, money_format)
            
            # Saldo pendiente (De la factura general, no de la línea)
            sheet.write(row, 9, move.amount_residual, money_format)
            
            row += 1

        workbook.close()
        output.seek(0)
        
        # 5. Preparar la descarga
        self.excel_file = base64.b64encode(output.read())
        self.file_name = f'Facturas_Impagas_{self.date_from}_{self.date_to}.xlsx'
        output.close()

        # 6. Retornar la vista del wizard recargada con el archivo listo
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'unpaid.invoice.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }