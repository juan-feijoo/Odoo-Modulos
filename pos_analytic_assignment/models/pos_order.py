# -*- coding: utf-8 -*-
from odoo import models

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _generate_pos_order_invoice(self):
        # 1. Dejamos que Odoo cree la factura de forma normal primero
        move = super()._generate_pos_order_invoice()

        # 2. Obtenemos la cuenta analítica desde la configuración de nuestro PoS
        # La ruta es: Pedido -> Sesión -> Configuración del PoS -> Nuestra Cuenta Analítica
        analytic_account = self.session_id.config_id.analytic_account_id
        
        # 3. Si se configuró una cuenta analítica para este PoS...
        if analytic_account:
            # 4. Recorremos cada línea de la factura recién creada
            for line in move.invoice_line_ids:
                # 5. Asignamos la distribución analítica a la línea si:
                #    SOLO a las líneas de ingresos/gastos (no a las de impuestos o deudores)
                #    y que no tengan ya una distribución asignada.
                if line.account_id.analytic_support and not line.analytic_distribution:
                    line.analytic_distribution = {
                        str(analytic_account.id): 100.0
                    }
        
        # 6. Devolvemos la factura ya modificada
        return move