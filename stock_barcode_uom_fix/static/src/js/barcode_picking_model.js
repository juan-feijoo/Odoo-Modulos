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
        
        async _processPackage(barcodeData) {
            console.log("====================================");
            console.log("[UOM_FIX] _processPackage INICIADO");
            // Imprimimos el paquete completo para ver su estructura exacta
            console.log("[UOM_FIX] barcodeData.package:", JSON.parse(JSON.stringify(barcodeData.package || {})));
            
            const patchedObjects =[];

            // SAFEGUARD CORREGIDO: Buscamos en 'quants' (objetos) y validamos el tipo
            if (barcodeData && barcodeData.package && Array.isArray(barcodeData.package.quants)) {
                for (const quant of barcodeData.package.quants) {
                    if (typeof quant === 'object' && quant !== null) {
                        // Si falta product_id, lo mockeamos para evitar el Cannot read properties of undefined
                        if (quant.product_id === undefined || quant.product_id === false) {
                            console.warn("[UOM_FIX] ⚠️ Quant sin product_id detectado:", quant);
                            const orig = quant.product_id;
                            quant.product_id = { id: false };
                            patchedObjects.push({ obj: quant, key: 'product_id', orig: orig });
                        }
                        // Por si el error viene de package_id
                        if (quant.package_id === undefined || quant.package_id === false) {
                            const orig = quant.package_id;
                            quant.package_id = { id: false };
                            patchedObjects.push({ obj: quant, key: 'package_id', orig: orig });
                        }
                    }
                }
            }

            // Mantenemos la protección de las líneas por seguridad
            if (this.currentState && Array.isArray(this.currentState.lines)) {
                for (const line of this.currentState.lines) {
                    if (typeof line === 'object' && line !== null) {
                        if (line.product_id === undefined || line.product_id === false) {
                            const orig = line.product_id;
                            line.product_id = { id: false };
                            patchedObjects.push({ obj: line, key: 'product_id', orig: orig });
                        }
                    }
                }
            }

            let result;
            try {
                // Llamada al método nativo
                result = await super._processPackage(...arguments);
            } catch (error) {
                console.error("[UOM_FIX] ❌ ERROR DENTRO DE _processPackage NATIVO:", error);
                throw error;
            } finally {
                // Restauramos los objetos a su estado original para no corromper la memoria de OWL
                for (const patch of patchedObjects) {
                    patch.obj[patch.key] = patch.orig;
                }
            }
            
            console.log("[UOM_FIX] ✅ _processPackage FINALIZADO CON ÉXITO");
            console.log("====================================");
            return result;
        },

        async _createLine(params) {
            const line = await super._createLine(...arguments);
            const { product } = params;
            
            if (product && this.currentState && this.currentState.lines) {
                const move = this.currentState.lines.find(l => l.product_id?.id === product.id && l.demand_qty > 0) ||
                             this.currentState.lines.find(l => l.product_id?.id === product.id);

                if (move && move.product_uom_id && move.product_uom_id !== product.uom_id) {
                    console.log("[UOM_FIX] _createLine - Heredando UdM especial del remito:", move.product_uom_id);
                    line.product_uom_id = move.product_uom_id;
                    if (this.units && this.units[move.product_uom_id]) {
                        line.product_uom = this.units[move.product_uom_id];
                    }
                }
            }
            return line;
        }
    });
}