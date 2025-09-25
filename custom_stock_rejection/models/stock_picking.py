# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # 1. Agregamos el nuevo estado 'rejected' a la lista de estados existentes.
    #    Usamos 'selection_add' para no sobreescribir los estados originales.
    state = fields.Selection(
        selection_add=[('rejected', 'Rechazado')],
        ondelete={'rejected': 'cascade'}
    )

    def action_reject(self):
        """
        Esta función se ejecuta al presionar el botón 'Rechazar'.
        Replica la lógica de cancelación y luego establece el estado a 'rechazado'.
        """
        # Verificamos que no se intente rechazar algo que ya está hecho o cancelado.
        if any(picking.state in ('done', 'cancel', 'rejected') for picking in self):
            raise UserError(_('No puedes rechazar una transferencia que ya está finalizada, cancelada o rechazada.'))

        # 2. Llamamos a la función interna que cancela los movimientos de stock.
        #    Esto es crucial: libera las cantidades reservadas.
        self._action_cancel()

        # 3. Establecemos nuestro estado personalizado 'rechazado'.
        self.write({'state': 'rejected'})

        return True