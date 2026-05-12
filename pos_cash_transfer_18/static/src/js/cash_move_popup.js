/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { CashMovePopup } from "@point_of_sale/app/navbar/cash_move_popup/cash_move_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";

patch(CashMovePopup.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        // Usamos this.pos.session como nos indicó el grep de Odoo 18
        this.branchJournals = (this.pos.session && this.pos.session.transfer_journal) ||[];

        onWillStart(async () => {
            // Si la precarga falló, intentamos recuperar los diarios directamente via ORM
            if (!this.branchJournals || this.branchJournals.length === 0) {
                console.log("Precarga vacía, intentando fallback via ORM...");
                try {
                    const journals = await this.orm.searchRead(
                        "account.journal",
                        [["use_supplier", "=", true]],
                        ["id", "name"]
                    );
                    this.branchJournals = journals;
                    console.log("Diarios cargados via fallback:", this.branchJournals);
                    
                    // Si después del fallback tenemos diarios y no hay selección, ponemos el primero
                    if (!this.state.branchJournalId && this.branchJournals.length) {
                        this.state.branchJournalId = this.branchJournals[0].id;
                    }
                } catch (error) {
                    console.error("Error en el fallback de diarios:", error);
                }
            }
        });

        // Inicialización inmediata si ya tenemos datos
        if (!this.state.branchJournalId && this.branchJournals.length) {
            this.state.branchJournalId = this.branchJournals[0].id;
        }
    },
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

        console.log("Tipo de movimiento a enviar a Python:", this.state.type);

        try {
            // AQUÍ ESTÁ LA MAGIA DEL GREP: this.pos.session.id
            await this.orm.call("pos.session", "try_cash_in_out", [
                [this.pos.session.id],
                this.state.type,
                amount,
                this.state.reason,
                extras,
            ]);
            this.notification.add("Movimiento de efectivo completado con éxito.", 3000);
        } catch (error) {
            console.error("Error durante el movimiento de efectivo:", error);
            this.notification.add("Falla al completar el movimiento de efectivo.", 3000);
        }
        this.props.close();
    },
});