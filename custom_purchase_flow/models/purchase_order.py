from odoo import models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model_create_multi
    def create(self, vals_list):

        records = super(PurchaseOrder, self).create(vals_list)

        for record in records:
            if record.requisition_id:
                attachments = self.env['ir.attachment'].search([
                    ('res_model', '=', 'purchase.requisition'),
                    ('res_id', '=', record.requisition_id.id)
                ])
                
                if attachments:
                    for attachment in attachments:
                        attachment.copy({
                            'res_model': 'purchase.order',
                            'res_id': record.id,
                        })
        
        return records

    def button_cancel(self):
        
        res = super(PurchaseOrder, self).button_cancel()

        for order in self:
            requisition = order.requisition_id
            if requisition and requisition.state == 'done':
                requisition.state = 'in_progress'
        return res