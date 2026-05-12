/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { CashMovePopup } from "@point_of_sale/app/navbar/cash_move_popup/cash_move_popup";


patch(CashMovePopup.prototype, {
    
    async confirm() {
        const amount = parseFloat(this.state.amount || 0);
        if (!amount) {
            this.notification.add("Please specify an amount.", 3000);
            return this.props.close();
        }

        const extras = {
            branch_journal_id: this.state.branchJournalId,
            reason: this.state.reason.trim(),
        };

        // 🐛 DEBUG: Verificamos en consola si es 'in' o 'out'
        console.log("Tipo de movimiento a enviar a Python:", this.state.type);

        try {
            await this.orm.call("pos.session", "try_cash_in_out", [[this.pos.pos_session.id],
                this.state.type, // <-- AQUÍ ESTÁ TU FIX: Envía 'in' u 'out' dinámicamente
                amount,
                this.state.reason,
                extras,
            ]);
            this.notification.add("Movimiento de efectivo completado con éxito.", 3000);
        } catch (error) {
            console.error("Ocurrió un error durante el movimiento:", error);
            this.notification.add("Falla al completar el movimiento de efectivo.", 3000);
        }
        this.props.close();
    },
});