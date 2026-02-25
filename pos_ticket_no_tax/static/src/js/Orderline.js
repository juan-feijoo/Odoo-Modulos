/** @odoo-module */

import { Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Orderline.prototype, {
    // Override get_taxes to prioritize product taxes over fiscal position taxes
    get_taxes() {
        // If the product has taxes defined, use them directly.
        // this.product.taxes_id contains an array of tax IDs (integers).
        // The original get_taxes() usually maps these IDs to actual tax objects.
        if (this.product && this.product.taxes_id && this.product.taxes_id.length > 0) {
            // Get the tax objects from the POS store's tax_by_id mapping
            const productTaxes = this.product.taxes_id.map(taxId => this.pos.taxes_by_id[taxId]);
            // Filter out any undefined taxes (e.g., if a tax was deleted)
            return productTaxes.filter(tax => tax);
        }

        // If no product taxes are defined, fall back to the original method,
        // which typically applies fiscal position rules.
        return super.get_taxes(...arguments);
    },
});
