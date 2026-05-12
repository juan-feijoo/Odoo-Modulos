from odoo import models, fields, _, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    counted_money_final = fields.Monetary(string='Transaction', readonly=True)

    def _load_pos_data(self, data):
        _logger.info("--- INICIANDO _load_pos_data EN POS_CASH_TRANSFER ---")
        
        res = super()._load_pos_data(data)
        
        domain = [('use_supplier', '=', True)]
        journals = self.env['account.journal'].sudo().search_read(
            domain, 
            ['id', 'name', 'company_id']
        )
        
        _logger.info(f"Diarios de transferencia encontrados: {len(journals)}")
        
        if res.get('data') and len(res['data']) > 0:
            res['data'][0]['transfer_journal'] = journals
        
        return res

    @api.depends('payment_method_ids', 'order_ids', 'cash_register_balance_start')
    def _compute_cash_balance(self):
        for session in self:
            _logger.info('Computing balance')
            cash_payment_method = session.payment_method_ids.filtered(lambda pm: pm.type == 'cash')[:1]
            if cash_payment_method:
                total_cash_payment = 0.0
                last_session = session.search([('config_id', '=', session.config_id.id), ('id', '<', session.id)], limit=1)
    
                result = self.env['pos.payment']._read_group(
                    [('session_id', '=', session.id), ('payment_method_id', '=', cash_payment_method.id)],
                    aggregates=['amount:sum']
                )
                total_cash_payment = result[0][0] or 0.0
                _logger.info(f"Total cash payment {total_cash_payment}")
                
                cash_journal = getattr(session, 'cash_journal_id', False) or cash_payment_method.journal_id
                
                cash_transfers = self.env['account.payment'].search([
                    ('pos_session_id', '=', session.id),
                    ('is_internal_transfer', '=', True),
                    ('journal_id', '=', cash_journal.id if cash_journal else False),
                ])
                
                total_transfer_out = sum(cash_transfers.filtered(lambda t: t.payment_type == 'outbound').mapped('amount'))
                total_transfer_in = sum(cash_transfers.filtered(lambda t: t.payment_type == 'inbound').mapped('amount'))
                
                net_transfer_out = total_transfer_out - total_transfer_in
                
                amount_kept = 0
                if session.cash_register_balance_end_real:
                    amount_kept = session.cash_register_balance_end_real
                    
                cash_real_transaction = sum(session.statement_line_ids.mapped('amount'))
                if session.state == 'closed':
                    total_entry_encoding = cash_real_transaction + total_cash_payment - net_transfer_out - amount_kept
                else:
                    total_entry_encoding = (
                        cash_real_transaction + total_cash_payment - net_transfer_out - amount_kept
                    )
                    _logger.info(f'Total entry encoding: {total_entry_encoding}')
                
                session.cash_register_balance_end = (
                    (last_session.cash_register_balance_end_real or 0.0)
                    + total_entry_encoding
                )
                session.cash_register_difference = session.cash_register_balance_end_real - session.cash_register_balance_end
            else:
                session.cash_register_balance_end = 0.0
                session.cash_register_difference = 0.0

    def try_cash_in_out(self, _type, amount, reason, extras):
        _logger.info("Starting try_cash_in_out method")
        _logger.info("Parameters received: _type=%s, amount=%s, reason=%s, extras=%s", _type, amount, reason, extras)
        
        for session in self:
            cash_journal = getattr(session, 'cash_journal_id', False)
            if not cash_journal:
                cash_payment_method = session.payment_method_ids.filtered(lambda pm: pm.type == 'cash')[:1]
                cash_journal = cash_payment_method.journal_id
            
            if not cash_journal:
                raise UserError(_("There is no cash payment method for this PoS Session."))
                
            if not cash_journal.default_account_id:
                raise UserError(_("The cash journal must have a default account configured."))
            
            if not extras.get('branch_journal_id'):
                raise UserError(_("A branch journal must be specified for the cash transfer."))
                
            try:
                branch_journal_id = int(extras['branch_journal_id'])
            except ValueError:
                raise UserError(_("Invalid branch journal ID: %s") % extras['branch_journal_id'])
                
            branch_journal = self.env['account.journal'].browse(branch_journal_id)
            if not branch_journal.default_account_id:
                raise UserError(_("The selected branch journal must have a default account configured."))
                
            safe_type = str(_type).strip().lower()
            is_cash_in = (safe_type == 'in')
            
            if branch_journal.company_id == session.company_id:
                _logger.info("Misma compañía: Creando transferencia interna directa.")
                payment = self.env['account.payment'].create({
                    'journal_id': cash_journal.id if not is_cash_in else branch_journal.id,
                    'destination_journal_id': branch_journal.id if not is_cash_in else cash_journal.id,
                    'date': fields.Date.context_today(self),
                    'memo': f"{session.name} - {'Entrada' if is_cash_in else 'Salida'} Caja Chica: {reason}", # CORREGIDO: memo en lugar de ref
                    'amount': amount,
                    'payment_type': 'outbound',
                    'pos_session_id': session.id,
                    'is_internal_transfer': True,
                })
                payment.action_post()
            else:
                _logger.info("Multi-compañía: Creando pagos cruzados.")
                destination_company = branch_journal.company_id
                
                transfer_journal = session.company_id.transfer_journal
                if not transfer_journal:
                    raise UserError("La compañía actual no tiene seleccionada una cuenta de transferencias")

                origin_payment_type = 'inbound' if is_cash_in else 'outbound'
                dest_payment_type = 'outbound' if is_cash_in else 'inbound'
                
                origin_ref = f"{session.name} - {'Entrada desde' if is_cash_in else 'Salida a'} Sucursal: {reason}"
                dest_ref = f"Transferencia {'saliente' if is_cash_in else 'entrante'} de: {session.company_id.name} - {reason}"

                payment_origin = self.env['account.payment'].create({
                    'journal_id': cash_journal.id,
                    'date': fields.Date.context_today(self),
                    'memo': origin_ref, # CORREGIDO: memo
                    'amount': amount,
                    'destination_journal_id': transfer_journal.id,
                    'payment_type': origin_payment_type,
                    'pos_session_id': session.id,
                    'is_internal_transfer': True,
                })
                payment_origin.action_post()
        
                payment_dest = self.env['account.payment'].sudo().with_company(destination_company).create({
                    'journal_id': branch_journal.id,
                    'date': fields.Date.context_today(self),
                    'memo': dest_ref, # CORREGIDO: memo
                    'amount': amount,
                    'destination_journal_id': destination_company.transfer_journal.id,
                    'payment_type': dest_payment_type,
                    'is_internal_transfer': True,
                    'pos_session_id': session.id,
                    'company_id': destination_company.id,
                })
                payment_dest.action_post()
            
    def post_closing_cash_details(self, data=None, **kwargs):
        _logger.info(f'Data received: {data} | kwargs: {kwargs}')

        # Compatibilidad por si llega como kwarg o como diccionario en data
        if not data:
            data = kwargs

        if isinstance(data, dict):
            counted_cash = float(str(data.get("counted_cash", "0")).replace(",", "."))
            reserve_cash = float(str(data.get("reserve_cash", "0")).replace(",", "."))
        else:
            counted_cash = float(data)
            reserve_cash = 0.0
        
        # IMPORTANTE: sudo() para evitar error de permisos al escribir en pos.config
        if reserve_cash:
            self.config_id.sudo().pos_keep_amount = reserve_cash
        else:
            self.config_id.sudo().pos_keep_amount = 0
            
        self.ensure_one()
        check_closing_session = self._cannot_close_session()
        if check_closing_session:
            return check_closing_session

        cash_journal_main = getattr(self, 'cash_journal_id', False) or self.payment_method_ids.filtered(lambda pm: pm.type == 'cash')[:1].journal_id
        if not cash_journal_main:
            raise UserError(_("There is no cash register in this session."))
    
        self.counted_money_final = counted_cash - reserve_cash
        balance_real = max(0, counted_cash - reserve_cash)
    
        _logger.info(f'Balance real: {balance_real}')
    
        sessions = self.filtered(lambda s: getattr(s, 'cash_journal_id', False) or s.payment_method_ids.filtered(lambda pm: pm.type == 'cash'))
        for session in sessions:
            cash_journal = getattr(session, 'cash_journal_id', False) or session.payment_method_ids.filtered(lambda pm: pm.type == 'cash')[:1].journal_id
            
            if not cash_journal.default_account_id:
                raise UserError(_("The cash journal must have a default account configured."))
            
            destination_company = self.env.company.transfer_destination_company_id or self.env['res.company'].browse(1).sudo()
            if not destination_company.exists():
                raise UserError(_("The selected destination company does not exist."))
                
            transfer_journal = self.env.company.transfer_journal
            if not transfer_journal:
                raise UserError("La compañía no tiene seleccionada una cuenta de transferencias")
                
            _logger.info("Creating transfer in origin company: %s", self.env.company.name)
            if balance_real > 0:
                payment_date = self.start_at.date() if self.start_at else fields.Date.context_today(self)
                payment_out = self.env['account.payment'].create({
                    'journal_id': cash_journal.id,
                    'date': payment_date,
                    'memo': f"{session.name} - Transferencia saliente a: {destination_company.name}",
                    'amount': balance_real,
                    'destination_journal_id': transfer_journal.id,
                    'payment_type': 'outbound',
                    'pos_session_id': session.id,
                    'is_internal_transfer': True,
                })
                payment_out.action_post()
        
                _logger.info("Creating transfer in destination company: %s", destination_company.name)
                payment_in = self.env['account.payment'].sudo().with_company(destination_company).create({
                    'journal_id': destination_company.cash_journal.id,
                    'date': payment_date,
                    'memo': f"Transferencia entrante de: {self.env.company.name}",
                    'amount': balance_real,
                    'destination_journal_id': destination_company.transfer_journal.id,
                    'payment_type': 'inbound',
                    'is_internal_transfer': True,
                    'pos_session_id': session.id,
                    'company_id': destination_company.id,
                })
                payment_in.action_post()
    
        self.cash_register_balance_end_real = self.config_id.pos_keep_amount
        return {'successful': True}