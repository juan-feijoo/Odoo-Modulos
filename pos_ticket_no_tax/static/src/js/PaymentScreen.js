/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    // Parche para aplicar la lógica de "Sin Impuestos" al entrar a la pantalla de pagos
    // si la orden no está marcada para facturar.
    setup() {
        super.setup();
        
        const order = this.currentOrder;
        
        // Ejecutamos la lógica de limpieza de impuestos si NO está marcada para facturar
        // Esto cubre el caso de entrar a pagos sin tocar el botón de factura.
        if (!order.is_to_invoice()) {
            this._applyNoTaxLogic(order);
        }
    },

    // Método de ayuda para aplicar la lógica de "Sin Impuestos"
    async _applyNoTaxLogic(order) {
        if (!order) return;

        // Iterar sobre todas las líneas de la orden y limpiar sus impuestos
        for (const line of order.get_orderlines()) {
            line.tax_ids = []; // Intenta limpiar la propiedad tax_ids directamente
        }
    },

    // Maneja el TOGGLE del botón "Factura"
    async toggleIsToInvoice() {
        // Ejecutar lógica original (cambio visual y booleano)
        await super.toggleIsToInvoice(...arguments);

        const order = this.currentOrder;
        if (!order) return;
        
        if (order.is_to_invoice()) {
            // CASO A: El usuario ACTIVÓ "Factura". Se deben aplicar impuestos.
            // Restaurar la posición fiscal del cliente si existe y reevaluar impuestos.
            const client = order.get_partner();
            if (client && client.property_account_position_id) {
                // Set the fiscal position of the order to the client's fiscal position
                await order.set_fiscal_position(client.property_account_position_id);
            } else {
                // If no specific client or fiscal position, clear any existing fiscal position
                // This will make orderlines use their default taxes.
                await order.set_fiscal_position(undefined);
            }

            // Iterar sobre todas las líneas de la orden y restaurar sus impuestos originales del producto.
            for (const line of order.get_orderlines()) {
                if (line.product && line.product.taxes_id) {
                    // Restaurar los tax_ids de la línea a los impuestos por defecto del producto
                    line.tax_ids = line.product.taxes_id;
                } else {
                    // Si el producto no tiene impuestos, asegurarse de que la lista de tax_ids esté vacía
                    line.tax_ids = [];
                }
                // Forzar la reevaluación de las cantidades y totales de esta línea de producto,
                // lo que a su vez recalculará los totales de la orden.
                line.set_quantity(line.quantity);
            }
        } else {
            // CASO B: El usuario DESACTIVÓ "Factura" (Ticket X).
            // Llamamos al helper para que elimine los impuestos directamente de las líneas.
            await this._applyNoTaxLogic(order);
        }
    }
});