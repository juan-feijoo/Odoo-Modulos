# -*- coding: utf-8 -*-
from odoo import models
import logging

_logger = logging.getLogger(__name__)

class AccountReport(models.Model):
    _inherit = 'account.report'

    def _find_consumidor_final_id(self):

        try:
            resp_type = self.env.ref('l10n_ar.res_afip_responsibility_type_5')
            partner = self.env['res.partner'].search([('afip_responsability_type_id', '=', resp_type.id)], limit=1)
            if partner:
                _logger.info("Partner 'Consumidor Final' encontrado por Tipo de Responsabilidad AFIP.")
                return partner.id
        except Exception:
            pass

        try:
            partner = self.env.ref('l10n_ar.res_partner_consumidor_final')
            if partner:
                _logger.info("Partner 'Consumidor Final' encontrado por XML ID.")
                return partner.id
        except Exception:
            pass # Si no existe el XML ID, pasamos al siguiente.

        partners = self.env['res.partner'].search([('name', 'ilike', 'Consumidor Final Anónimo')], limit=1)
        if partners:
            _logger.warning("Partner 'Consumidor Final' encontrado por nombre. Se recomienda configurar el Tipo de Responsabilidad AFIP para mayor fiabilidad.")
            return partners.id

        _logger.warning("No se pudo determinar un partner 'Consumidor Final'. Las facturas a este podrían no procesarse como esperado.")
        return None


    def get_expanded_lines(self, options, line_id, *args, **kwargs):

        lines = super().get_expanded_lines(options, line_id, *args, **kwargs)

        consumidor_final_id = self._find_consumidor_final_id()

        for line in lines:
            caret_type = line.get('caret_options')
            if caret_type not in ('account.move.line', 'account.payment'):
                continue

            try:
                aml_id_str = line['id'].split('~account.move.line~')[-1]
                aml_id = int(aml_id_str)
                move_line = self.env['account.move.line'].browse(aml_id)
                
                cuit = ''
                partner_found = move_line.partner_id
                
                if partner_found:

                    if consumidor_final_id and partner_found.id == consumidor_final_id:
                        cuit = ''

                    else:
                        cuit = partner_found.vat or ''
                

                else:
                    current_company = move_line.company_id
                    if current_company.partner_id:
                         cuit = current_company.partner_id.vat or ''


                for column in line.get('columns', []):
                    if column.get('expression_label') == 'cuit':
                        column['name'] = cuit
                        break
                            
            except (ValueError, IndexError, KeyError) as e:
                _logger.error(f"[ERROR] Error procesando CUIT para línea ID {line.get('id')}: {e}")
        
        return lines