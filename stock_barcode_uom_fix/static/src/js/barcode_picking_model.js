/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import * as BarcodePickingModelModule from "@stock_barcode/models/barcode_picking_model";

let BarcodePickingModel = BarcodePickingModelModule.BarcodePickingModel || BarcodePickingModelModule.default;

if (!BarcodePickingModel) {
    const symbols = Object.getOwnPropertySymbols(BarcodePickingModelModule);
    for (const sym of symbols) {
        if (BarcodePickingModelModule[sym].name === 'BarcodePickingModel' || sym.toString() === 'Symbol(default)') {
            BarcodePickingModel = BarcodePickingModelModule[sym];
            break;
        }
    }
}

if (BarcodePickingModel) {
    patch(BarcodePickingModel.prototype, {
        
        async _findLine(barcodeData) {
            const { product } = barcodeData;
            return super._findLine(...arguments);
        },

        async _createLine(params) {
            const line = await super._createLine(...arguments);
            const { product } = params;
            
            if (product && this.currentState && this.currentState.lines) {
                const move = this.currentState.lines.find(l => l.product_id.id === product.id && l.demand_qty > 0) ||
                             this.currentState.lines.find(l => l.product_id.id === product.id);

                if (move && move.product_uom_id && move.product_uom_id !== product.uom_id) {
                    console.log("[UOM_FIX] _createLine - Heredando UdM especial del remito");
                    line.product_uom_id = move.product_uom_id;
                    line.product_uom = this.units[move.product_uom_id];
                }
            }
            return line;
        }
    });
}