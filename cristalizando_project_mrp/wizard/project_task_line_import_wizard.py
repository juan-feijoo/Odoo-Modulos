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

    task_id = fields.Many2one('project.task', string='Tarea', required=True, default=lambda self: self.env.context.get('active_id'))
    excel_file = fields.Binary(string='Archivo Excel', required=True)
    excel_filename = fields.Char(string='Nombre del Archivo')

    def import_lines(self):
        """Procesa el archivo Excel y crea las líneas de tarea."""
        if not self.excel_file:
            raise UserError("Por favor, carga un archivo Excel antes de importar.")

        # Leer el archivo Excel
        try:
            data = base64.b64decode(self.excel_file)
            file = io.BytesIO(data)
            df = pd.read_excel(file, sheet_name="EXPORTACION ODOO", engine='openpyxl')
        except ValueError:
            raise UserError("No se encontró la hoja 'EXPORTACION ODOO' en el archivo Excel.")
        except Exception as e:
            raise UserError(f"Error al leer el archivo Excel: {str(e)}")

        # Filtrar filas no deseadas
        df = df.dropna(how='all')
        if 'CANTIDAD' in df.columns:
            df = df[df['CANTIDAD'] != 0]
        
        def is_row_invalid(row):
            return all(str(cell).strip() in ['', ' '] for cell in row)
        df = df[~df.apply(is_row_invalid, axis=1)]
        
        # Validar columnas requeridas
        required_columns = [
            'TIPOLOGIA', 'CANTIDAD', 'CODIGO', 'DESCRIPCION', 
            'PRECIO UNITARIO CARPINTERIA', 'CODIGO DISTANCIA /KM', 
            'PRECIO UNITARIO INSTALACION', 'SUBTOTAL UNIDAD', 'SUBTOTAL','NOMBRE DEL PRODUCTO'
        ]
        for column in required_columns:
            if column not in df.columns:
                raise UserError(f"El archivo Excel debe contener la columna '{column}'")

        # Convertir campos numéricos
        try:
            df['CANTIDAD'] = pd.to_numeric(df['CANTIDAD'], errors='coerce').fillna(0)
            df['SUBTOTAL UNIDAD'] = pd.to_numeric(df['SUBTOTAL UNIDAD'], errors='coerce').fillna(0)
            df['SUBTOTAL'] = pd.to_numeric(df['SUBTOTAL'], errors='coerce').fillna(0)
            df['PRECIO UNITARIO CARPINTERIA'] = pd.to_numeric(df['PRECIO UNITARIO CARPINTERIA'], errors='coerce').fillna(0)
        except Exception as e:
            raise UserError(f"Error procesando los campos numéricos: {str(e)}")

        # Usamos la Unidad de Medida "Unit" como fallback.
        uom_unit = self.env.ref('uom.product_uom_unit')
        lines_to_create = []

        # Procesar las filas del archivo
        for index, row in df.iterrows():
            if row.isnull().all():
                continue
            
            if str(row['TIPOLOGIA']).strip().upper() == "FIN":
                break

            # Validar campos obligatorios
            required_fields = {
                'CODIGO': row['CODIGO'],
                'CANTIDAD': row['CANTIDAD'],
                'SUBTOTAL UNIDAD': row['SUBTOTAL UNIDAD'],
                'SUBTOTAL': row['SUBTOTAL'],
                'TIPOLOGIA': row['TIPOLOGIA'],
                'PRECIO UNITARIO CARPINTERIA': row['PRECIO UNITARIO CARPINTERIA'],
                'CODIGO DISTANCIA /KM': row['CODIGO DISTANCIA /KM'],
                'PRECIO UNITARIO INSTALACION': row['PRECIO UNITARIO INSTALACION'],
            }

            required_not_zero = ['TIPOLOGIA', 'CODIGO', 'DESCRIPCION', 'NOMBRE DEL PRODUCTO']
            for column in required_not_zero:
                if str(row[column]).strip() == '0':
                    raise UserError(f"El campo '{column}' no puede ser '0'. Error en la fila {index + 2}.")
        
            for field_name, value in required_fields.items():
                if value != 0 and field_name != 'CODIGO':
                    if str(value) == '#VALUE!':
                        raise UserError(f"Error '#VALUE!' en el campo '{field_name}'. Error en la fila {index + 2}.")
                    if not value:
                        raise UserError(f"El campo '{field_name}' no debe estar vacío. Error en la fila {index + 2}.")
                
            # Validar cálculos y formato numérico
            try:
                cantidad = float(row['CANTIDAD'])
                subtotal_unidad = float(row['SUBTOTAL UNIDAD'])
                subtotal = float(row['SUBTOTAL'])
                
                # Usamos round() para evitar problemas de precisión con floats
                if round(cantidad * subtotal_unidad, 2) != round(subtotal, 2):
                    raise UserError(
                        f"El subtotal calculado ({cantidad * subtotal_unidad:.2f}) no coincide con el valor proporcionado ({subtotal}). "
                        f"Error en la fila {index + 2}."
                    )
            except ValueError as e:
                raise UserError(f"Error de formato numérico en la fila {index + 2}: {e}.")
        
            # Buscar o crear el producto
            product_code = str(row['CODIGO']).strip()
            product = self.env['product.product'].search([('default_code', '=', product_code)], limit=1)
            if not product:
                product = self.env['product.product'].create({
                    'name': row.get('NOMBRE DEL PRODUCTO', 'Prod Finalizado sin nombre'),
                    'x_studio_descripcion': row.get('DESCRIPCION','Sin descripción'),
                    'default_code': product_code,
                    'uom_id': uom_unit.id,
                    'uom_po_id': uom_unit.id,
                    'categ_id': 16036, # ¡OJO! Este ID puede no existir en tu base de datos.
                    'purchase_method': "receive",
                    'list_price': subtotal_unidad,
                })

            # Preparar los valores para crear la línea de tarea
            vals = {
                'task_id': self.task_id.id,
                'product_id': product.id,
                'quantity': cantidad,
                'price_unit': subtotal_unidad,
                'x_studio_descripcion': row.get('DESCRIPCION','Sin descripción'),
                'x_studio_tipologia': row['TIPOLOGIA'],
                'x_studio_precio_unitario_carpinteria': row['PRECIO UNITARIO CARPINTERIA'],
                'x_studio_codigo_distancia_km': row['CODIGO DISTANCIA /KM'],
                'x_studio_precio_unitario_instalacion': row['PRECIO UNITARIO INSTALACION'],
            }
            lines_to_create.append(vals)

        # Crear todas las líneas en una sola operación
        if lines_to_create:
            self.env['project.task.line'].create(lines_to_create)

        return {'type': 'ir.actions.act_window_close'}