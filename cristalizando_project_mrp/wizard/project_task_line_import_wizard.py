
import base64
import io
import pandas as pd
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ProjectTaskLineImportWizard(models.TransientModel):
    _name = 'project.task.line.import.wizard'
    _description = 'Wizard para importar insumos a líneas de tarea desde Excel'

    task_id = fields.Many2one('project.task', string='Tarea', required=True)
    excel_file = fields.Binary(string='Archivo Excel', required=True)
    excel_filename = fields.Char(string='Nombre del Archivo')

    def import_lines(self):
        if not self.excel_file:
            raise UserError('Por favor, carga un archivo Excel antes de importar.')

        try:
            data = base64.b64decode(self.excel_file)
            file = io.BytesIO(data)
            df = pd.read_excel(file, sheet_name="EXPORTACION ODOO")
        except ValueError:
            raise UserError("No se encontró la hoja 'EXPORTACION ODOO' en el archivo Excel.")
        except Exception as e:
            raise UserError(f"Error al leer el archivo Excel: {str(e)}")

        df = df.dropna(how='all')
        if 'CANTIDAD' in df.columns:
            df = df[df['CANTIDAD'] != 0]

        def is_row_invalid(row):
            return all(str(cell).strip() in ['', ' '] for cell in row)
        df = df[~df.apply(is_row_invalid, axis=1)]

        required_columns = [
            'TIPOLOGIA', 'CANTIDAD', 'CODIGO', 'DESCRIPCION', 
            'PRECIO UNITARIO CARPINTERIA', 'CODIGO DISTANCIA /KM', 
            'PRECIO UNITARIO INSTALACION', 'SUBTOTAL UNIDAD', 'SUBTOTAL','NOMBRE DEL PRODUCTO'
        ]
        for column in required_columns:
            if column not in df.columns:
                raise UserError(f"El archivo Excel debe contener la columna '{column}'")

        # Convertir campos numéricos y manejar valores inválidos
        df['CANTIDAD'] = pd.to_numeric(df['CANTIDAD'], errors='coerce').fillna(0)
        df['SUBTOTAL UNIDAD'] = pd.to_numeric(df['SUBTOTAL UNIDAD'], errors='coerce').fillna(0)
        df['SUBTOTAL'] = pd.to_numeric(df['SUBTOTAL'], errors='coerce').fillna(0)
        df['PRECIO UNITARIO CARPINTERIA'] = pd.to_numeric(df['PRECIO UNITARIO CARPINTERIA'], errors='coerce').fillna(0)

        for index, row in df.iterrows():
            # Buscar o crear el producto
            product = self.env['product.product'].search([('default_code', '=', row['CODIGO'])], limit=1)
            if not product:
                product = self.env['product.product'].create({
                    'name': row.get('NOMBRE DEL PRODUCTO', 'Sin nombre'),
                    'default_code': row['CODIGO'],
                    'uom_id': 27, # Ajustar el id segun la base 
                    'uom_po_id': 27,
                })

            vals = {
                'task_id': self.task_id.id,
                'product_id': product.id,
                'quantity': row['CANTIDAD'],
                'tipologia': row['TIPOLOGIA'],
                'codigo': row['CODIGO'],
                'descripcion': row['DESCRIPCION'],
                'precio_unitario_carpinteria': row['PRECIO UNITARIO CARPINTERIA'],
                'codigo_distancia_km': row['CODIGO DISTANCIA /KM'],
                'precio_unitario_instalacion': row['PRECIO UNITARIO INSTALACION'],
                'subtotal_unidad': row['SUBTOTAL UNIDAD'],
                'subtotal': row['SUBTOTAL'],
                'nombre_producto': row['NOMBRE DEL PRODUCTO'],
            }
            self.env['project.task.line'].create(vals)
        return {'type': 'ir.actions.act_window_close'}
