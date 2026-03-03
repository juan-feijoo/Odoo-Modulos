from odoo import models, fields, api
import io
import base64
import xlsxwriter

class SaleReportWizard(models.TransientModel):
    _name = 'sale.report.wizard'
    _description = 'Asistente de Reporte de Ventas por Oportunidad'

    # Funciones para valores por defecto dinámicos (Año en curso)
    def _default_date_start(self):
        return fields.Date.today().replace(month=1, day=1)

    def _default_date_end(self):
        return fields.Date.today().replace(month=12, day=31)

    # Campos de configuración con fechas dinámicas
    date_start = fields.Date(string='Fecha Inicio', default=_default_date_start, required=True)
    date_end = fields.Date(string='Fecha Fin', default=_default_date_end, required=True)
    
    # Campos para la gestión del archivo generado
    excel_file = fields.Binary(string='Archivo Excel', readonly=True)
    file_name = fields.Char(string='Nombre del Archivo', readonly=True)
    state = fields.Selection([
        ('choose', 'Seleccionar Parámetros'),
        ('get', 'Descargar Archivo')
    ], string='Estado', default='choose')

    def action_generate_excel(self):
        # 1. Búsqueda en sale.order.line usando las fechas seleccionadas en el Wizard
        domain = [
            ('order_id.state', 'in', ['sale', 'done']),
            ('order_id.date_order', '>=', self.date_start),
            ('order_id.date_order', '<=', self.date_end),
            ('order_id.opportunity_id', '!=', False) # Filtro clave: Solo obras provenientes de CRM
        ]
        lines = self.env['sale.order.line'].search(domain)

        # 2. Preparación del Excel en memoria
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Ventas Obras')

        # Estilos
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
        
        # 3. Cabeceras
        headers =['ID VENTA', 'PRODUCTO', 'DESCRIPCION', 'TIPOLOGIA', 'CANTIDAD', 'CODIGO DISTANCIA/KM']
        for col_num, header in enumerate(headers):
            sheet.write(0, col_num, header, header_format)

        # Ajustamos el ancho de las columnas para que se vea prolijo
        sheet.set_column('A:A', 15)
        sheet.set_column('B:C', 35)
        sheet.set_column('D:F', 20)

        # 4. Volcado de datos
        row_num = 1
        for line in lines:
            # Limpiamos el "False" de la Tipología por si está vacía
            tipologia_raw = getattr(line, 'x_studio_tipologia', '') 
            tipologia = '' if tipologia_raw is False else str(tipologia_raw)

            # Traemos el Código Distancia directamente de la línea
            distancia_raw = getattr(line, 'x_studio_codigo_distancia_km', '') 
            distancia = '' if distancia_raw is False else distancia_raw

            # Traemos la Descripción de Studio (NUEVO)
            desc_raw = getattr(line, 'x_studio_descripcion', '')
            descripcion = '' if desc_raw is False else str(desc_raw)

            sheet.write(row_num, 0, line.order_id.name)
            sheet.write(row_num, 1, line.product_id.display_name or '')
            sheet.write(row_num, 2, descripcion) # Reemplazamos line.name por tu variable
            sheet.write(row_num, 3, tipologia)
            sheet.write(row_num, 4, line.product_uom_qty)
            sheet.write(row_num, 5, distancia) 
            
            row_num += 1

        workbook.close()
        
        # 5. Codificación y guardado del archivo
        excel_data = base64.b64encode(output.getvalue())
        output.close()

        # Generamos un nombre de archivo dinámico basado en las fechas elegidas
        generated_filename = f'Reporte_Ventas_{self.date_start}_al_{self.date_end}.xlsx'

        self.write({
            'excel_file': excel_data,
            'file_name': generated_filename,
            'state': 'get'
        })

        # 6. Recargamos la vista para mostrar la etapa de descarga
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }