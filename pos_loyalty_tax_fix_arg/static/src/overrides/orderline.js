/** @odoo-module */

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

/**
 * Función auxiliar para detectar impuestos internos.
 */
function isInternalTax(name) {
    if (!name) return false;
    const lowerName = name.toLowerCase();
    const searchPatterns = ["impuesto interno", "imp interno", "imp. interno"];
    return searchPatterns.some(pattern => lowerName.includes(pattern));
}

patch(Order.prototype, {
    _getRewardLineValues(args) {
        const lines = super._getRewardLineValues(...arguments);
        const reward = args.reward;
        
        if (reward && reward.reward_type === 'discount' && lines && lines.length > 0) {
            const totalDiscount = lines.reduce((sum, line) => sum + (line.price || 0), 0);
            const mergedLine = { ...lines[0] };
            mergedLine.price = totalDiscount;
            const product = mergedLine.product;
            if (product && product.taxes_id) {
                mergedLine.tax_ids = product.taxes_id;
            }
            return [mergedLine];
        }
        return lines;
    },

    /**
     * Sobrescribimos el resumen de impuestos para agrupar todos los "Internos" en una sola línea.
     * Forzamos amount_type: 'fixed' para que el ticket imprima el NOMBRE y no el porcentaje.
     */
    get_tax_details() {
        const details = super.get_tax_details(...arguments);
        const grouped_details = [];
        let internal_tax_amount = 0;
        let internal_tax_base = 0;
        let has_internal = false;

        for (const tax of details) {
            if (isInternalTax(tax.name) || (tax.tax && isInternalTax(tax.tax.name))) {
                internal_tax_amount += tax.amount;
                internal_tax_base += (tax.base || 0);
                has_internal = true;
            } else {
                grouped_details.push(tax);
            }
        }

        if (has_internal) {
            grouped_details.push({
                name: "Impuesto interno",
                amount: internal_tax_amount,
                base: internal_tax_base,
                tax: { 
                    id: 999999, // ID ficticio para evitar errores de KEY en OWL
                    name: "Impuesto interno", 
                    amount: 0, 
                    amount_type: 'fixed', // CRÍTICO: Fuerza al ticket a usar el nombre en lugar de "0%"
                    letter: '' 
                }
            });
        }

        return grouped_details;
    }
});

patch(Orderline.prototype, {
    getDisplayData() {
        const data = super.getDisplayData();
        if (data.tax_ids) {
            for (const tax of data.tax_ids) {
                if (isInternalTax(tax.name)) {
                    tax.name = "Impuesto interno";
                }
            }
        }
        return data;
    }
});
