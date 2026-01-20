import xmlrpc.client

# --- CONFIGURACIÓN DE CONEXIÓN ---
url = "https://outsourcearg-lafrancisca-prueba-25978354.dev.odoo.com"
db = "outsourcearg-lafrancisca-prueba-25978354"
username = "api.ia@tudominio.com"
api_key = "5a2f1660ecfe27b3ed4c70188eb22061b3545aa9"


datos_entrada = {
  "partner_id": 61840,           # ID del proveedor existente
  "journal_id": 214,             # ID del diario específico (No Fiscal)
  "date": "2025-11-20",          # Fecha contable
  "invoice_date": "2025-11-20",  # Fecha de factura
  "ref": "FAC-TEST-001",         # Referencia
  "invoice_line_ids": [
    {
      "product_id": 1,           # ID Producto A (Asegúrate que exista)
      "name": "Producto Prueba A",
      "quantity": 2.0,
      "price_unit": 100.0,
    },
    {
      "product_id": 2,           # ID Producto B (Asegúrate que exista)
      "name": "Producto Prueba B",
      "quantity": 1.0,
      "price_unit": 500.0,
    }
  ]
}

# Hay que convertirla a una lista de tuplas (0, 0, values).

lineas_odoo = []
for linea in datos_entrada["invoice_line_ids"]:
    lineas_odoo.append((0, 0, {
        "product_id": linea["product_id"],
        "name": linea["name"],
        "quantity": linea["quantity"],
        "price_unit": linea["price_unit"],
        # Opcional: Si el diario es no fiscal
        # "tax_ids": [] 
    }))


factura_vals = {
    "move_type": "in_invoice", # Fijo: Factura de Proveedor
    "partner_id": datos_entrada["partner_id"],
    "journal_id": datos_entrada["journal_id"],
    "date": datos_entrada["date"],
    "invoice_date": datos_entrada["invoice_date"],
    "ref": datos_entrada["ref"],
    "invoice_line_ids": lineas_odoo
}

# --- ENVÍO A ODOO ---
try:
    print("Conectando")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, api_key, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    if uid:
        print(f" Creando factura en Diario ID {datos_entrada['journal_id']}...")
        
        invoice_id = models.execute_kw(db, uid, api_key, 'account.move', 'create', [factura_vals])
        
        print(f" Factura creada con ID: {invoice_id}")
    else:
        print(" Error de autenticación.")

except xmlrpc.client.Fault as error:
    print("\nERROR DE ODOO:")
    print(f"Código: {error.faultCode}")
    print(f"Mensaje: {error.faultString}")
    # Tip común: Si falla aquí con el diario 214, verifica que sea de tipo 'purchase'
except Exception as e:
    print(f"\nERROR DE PYTHON: {e}")
