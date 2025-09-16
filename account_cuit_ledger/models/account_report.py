# -- coding: utf-8 --
import logging
from odoo import models, http


_logger = logging.getLogger(__name__)


class AccountReport(models.Model):
    _inherit = 'account.report'

    # ... (los métodos _find_consumidor_final_id y _add_cuit_to_report_lines no cambian) ...
    def _find_consumidor_final_id(self):
        try:
            resp_type = self.env.ref('l10n_ar.res_afip_responsibility_type_5')
            partner = self.env['res.partner'].search([('afip_responsability_type_id', '=', resp_type.id)], limit=1)
            if partner:
                return partner.id
        except Exception:
            pass
        try:
            partner = self.env.ref('l10n_ar.res_partner_consumidor_final')
            if partner:
                return partner.id
        except Exception:
            pass
        partners = self.env['res.partner'].search([('name', 'ilike', 'Consumidor Final Anónimo')], limit=1)
        if partners:
            return partners.id
        return None

    def _add_cuit_to_report_lines(self, lines):
        consumidor_final_id = self._find_consumidor_final_id()
        for line in lines:
            if not isinstance(line.get('id'), str) or 'account.move.line' not in line.get('id'):
                continue
            try:
                aml_id_str = line['id'].split('~account.move.line~')[-1]
                aml_id = int(aml_id_str)
                move_line = self.env['account.move.line'].browse(aml_id)
                if not move_line.exists():
                    continue
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

    def _get_lines(self, *args, **kwargs):
        """
        Solo agrega el CUIT a las líneas, sin modificar el colapsado/desplegado.
        """
        lines = super()._get_lines(*args, **kwargs)
        lines_with_cuit = self._add_cuit_to_report_lines(lines)
        return lines_with_cuit

    def get_expanded_lines(self, options, line_id, *args, **kwargs):
        lines = super().get_expanded_lines(options, line_id, *args, **kwargs)
        lines_with_cuit = self._add_cuit_to_report_lines(lines)
        return lines_with_cuit