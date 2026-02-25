/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);

        // Check if the current order is NOT to be invoiced
        if (!this.to_invoice) {
            // Add a flag to headerData for the receipt template to conditionally hide tax info
            result.headerData = result.headerData || {};
            result.headerData.is_no_iva_receipt = true;

            // Clear tax details from the data sent to the receipt template
            result.tax_details = [];
            
            // Explicitly set total tax to 0
            result.amount_tax = 0; 

            // Ensure amount_total reflects the untaxed total when taxes are removed
            if (result.amount_total !== undefined && result.amount_tax !== undefined) {
                // Only adjust if amount_total was computed with tax.
                // It should already be adjusted from line.tax_ids = [] but good for consistency.
                result.amount_total = this.get_total_without_tax(); // Use order's own method for untaxed total
            }
            // Ensure amount_total is passed correctly even if amount_untaxed is not directly available
            // result.amount_total = result.amount_total - result.amount_tax; // this line is usually not needed as amount_total should be the final result.

            // Also clear individual line taxes if they are part of result.orderlines
            if (result.orderlines) {
                result.orderlines.forEach(line => {
                    line.tax_ids = [];
                    // line.taxes and line.tax_amount are usually derived from tax_ids
                    // so explicitly clearing tax_ids should be sufficient.
                });
            }
        }
        return result;
    },
});