/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { useService } from "@web/core/utils/hooks";

patch(ClosePosPopup.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state.reserve_cash = 0;
    },

    async closeSession() {
        if (this.pos.config.cash_control) {
            try {
                const cash_payment_method = Object.values(this.state.payments).find(p => p.type === 'cash');
                const counted_cash = cash_payment_method ? cash_payment_method.counted : 0;

                await this.orm.call("pos.session", "post_closing_cash_details", [
                    [this.pos.session.id], // <--- ¡CORREGIDO: Ahora sí es un Array!
                    {
                        counted_cash: counted_cash,
                        reserve_cash: parseFloat(this.state.reserve_cash || 0),
                    },
                ]);
            } catch (error) {
                console.error("Error al procesar reserva de efectivo:", error);
                this.notification.add("Error al procesar la reserva de efectivo.", 3000);
            }
        }
        
        await super.closeSession(...arguments);
    },
});