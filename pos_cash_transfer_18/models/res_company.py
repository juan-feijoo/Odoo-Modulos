from odoo import models, fields, _,api
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = "res.company"

    cash_journal = fields.Many2one(
        'account.journal',
        string='Diario efectivo',
        domain=[('type', '=', 'cash')],
        help='Diario que se usara para enviar/recibir transferencias entre compañias.'
    )

    transfer_journal = fields.Many2one(
        'account.journal',
        string='Diario transferencias',
        domain=[('type', 'in', ['bank', 'cash'])],
        help='Diario para anotar las transferencias'
    )

    transfer_destination_company_id = fields.Many2one(
        'res.company',
        string='Compañía de destino',
        help='Compañía a la que se enviarán las transferencias de efectivo por defecto.'
    )

