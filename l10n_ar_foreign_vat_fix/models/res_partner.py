# -*- coding: utf-8 -*-
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def onchange(self, values, field_name, field_onchange):
        original_vat = values.get('vat') if isinstance(values, dict) else False
        _logger.info("ONCHANGE INICIO - original_vat: %s, field_name: %s", original_vat, field_name)
    
        result = super(ResPartner, self).onchange(values, field_name, field_onchange)
    
        if original_vat and isinstance(result, dict) and result.get('value') and 'vat' in result['value']:
            if result['value']['vat'] != original_vat:
                # 1. Intentar obtener el ID del tipo de identificación desde values
                id_type_id = values.get('l10n_latam_identification_type_id')
                if isinstance(id_type_id, (list, tuple)) and id_type_id:
                    id_type_id = id_type_id[0]
                
                # 2. Si no está en values, tomarlo del registro actual (si existe)
                if not id_type_id and self:
                    id_type_id = self.l10n_latam_identification_type_id.id
    
                _logger.info("ONCHANGE - id_type_id detectado: %s", id_type_id)
    
                if id_type_id:
                    id_type = self.env['l10n_latam.identification.type'].browse(id_type_id)
                    if id_type.l10n_ar_afip_code in ['99', '91']:
                        result['value']['vat'] = original_vat
                        _logger.info("ONCHANGE RESTAURADO: Se evitó que Odoo cambie '%s' a '%s'",
                                     original_vat, result['value']['vat'])
    
        _logger.info("ONCHANGE FIN - resultado vat: %s", 
                     result.get('value', {}).get('vat') if isinstance(result, dict) else 'N/A')
        return result

    def _sanitize_vat(self, vat):
        """
        Sobrescribimos la sanitización para evitar que elimine caracteres
        no numéricos en IDs extranjeras (AFIP 99, 91).
        """
        partner_id_type = self.l10n_latam_identification_type_id
        _logger.info("_sanitize_vat llamado - vat: %s, partner_id_type: %s (code: %s)",
                     vat, partner_id_type.name if partner_id_type else 'None',
                     partner_id_type.l10n_ar_afip_code if partner_id_type else 'None')

        if partner_id_type and partner_id_type.l10n_ar_afip_code in ['99', '91']:
            _logger.info("_sanitize_vat OMITIDO (ID Extranjera): retornando %s", vat)
            return vat

        # Para el resto de los casos, se ejecuta la sanitización estándar
        result = super(ResPartner, self)._sanitize_vat(vat)
        _logger.info("_sanitize_vat ESTÁNDAR - entrada: %s, salida: %s", vat, result)
        return result

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info(" CREATE llamado con %d registros", len(vals_list))
        for idx, vals in enumerate(vals_list):
            _logger.info(" CREATE vals[%d]: vat=%s, id_type=%s",
                         idx, vals.get('vat'), vals.get('l10n_latam_identification_type_id'))

        has_foreign = False
        for vals in vals_list:
            if vals.get('vat') and vals.get('l10n_latam_identification_type_id'):
                id_type = self.env['l10n_latam.identification.type'].browse(vals['l10n_latam_identification_type_id'])
                if id_type.l10n_ar_afip_code in ['99', '91']:
                    has_foreign = True
                    _logger.info(" CREATE detectado ID Extranjero para vat: %s", vals.get('vat'))
                    break

        if has_foreign:
            self = self.with_context(no_vat_validation=True)
            _logger.info(" CREATE aplicando contexto no_vat_validation=True")

        result = super(ResPartner, self).create(vals_list)
        _logger.info(" CREATE finalizado - VAT guardado: %s", result.mapped('vat'))
        return result

    def write(self, vals):
        _logger.info(" WRITE llamado para IDs: %s, vals: %s", self.ids, vals)

        if 'vat' not in vals:
            _logger.info(" WRITE sin cambio en vat, delegando a super")
            return super().write(vals)

        foreign_partners = self.env['res.partner']
        local_partners = self.env['res.partner']

        for record in self:
            id_type_id = vals.get('l10n_latam_identification_type_id', record.l10n_latam_identification_type_id.id)
            is_foreign = False

            if id_type_id:
                id_type = self.env['l10n_latam.identification.type'].browse(id_type_id)
                if id_type.l10n_ar_afip_code in ['99', '91']:
                    is_foreign = True
                    _logger.info(" WRITE partner ID %s es extranjero (code %s)", record.id, id_type.l10n_ar_afip_code)

            if is_foreign:
                foreign_partners |= record
            else:
                local_partners |= record

        res = True
        if foreign_partners:
            _logger.info(" WRITE aplicando contexto no_vat_validation a %s partners", len(foreign_partners))
            res &= super(ResPartner, foreign_partners.with_context(no_vat_validation=True)).write(vals)
        if local_partners:
            _logger.info(" WRITE sin contexto especial para %s partners", len(local_partners))
            res &= super(ResPartner, local_partners).write(vals)

        _logger.info(" WRITE finalizado - resultado: %s", res)
        return res