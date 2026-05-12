/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import * as MainModule from "@stock_barcode/components/main";

let MainComponent = MainModule.MainComponent || MainModule.default;

if (!MainComponent) {
    const symbols = Object.getOwnPropertySymbols(MainModule);
    const defaultSymbol = symbols.find(s => s.toString() === "Symbol(default)");
    if (defaultSymbol) {
        MainComponent = MainModule[defaultSymbol];
    }
}

if (MainComponent) {
    patch(MainComponent.prototype, {
        
        async finalizarPreparacion() {
            // FIX: En Odoo 18 accedemos al modelo a través del entorno (env)
            const model = this.env.model; 
            if (!model || !model.record) {
                console.error("No se encontró el modelo en this.env.model");
                return;
            }

            const recordId = model.record.id;
            
            try {
                // 1. Guardamos cualquier escaneo pendiente antes de cambiar de fase
                if (model.isDirty) {
                    await model.save();
                }

                // 2. Llamada al ORM
                await this.env.services.orm.call(
                    "stock.picking", 
                    "action_barcode_finalizar_preparacion", 
                    [[recordId]]
                );
                
                this.env.services.notification.add("Preparación finalizada con éxito", { 
                    type: "success" 
                });

                // 3. Recargamos la interfaz para que evalúe los nuevos botones
                // En la app de código de barras, recargar la vista es la forma más limpia 
                // de reevaluar todo el estado sin romper la reactividad de Owl.
                window.location.reload();
                
            } catch (error) {
                console.error("Error en finalizarPreparacion:", error);
            }
        },
        
        async iniciarRepaso() {
            const model = this.env.model;
            if (!model || !model.record) {
                console.error("No se encontró el modelo en this.env.model");
                return;
            }

            const recordId = model.record.id;
            
            try {
                if (model.isDirty) {
                    await model.save();
                }

                await this.env.services.orm.call(
                    "stock.picking", 
                    "action_barcode_iniciar_repaso", 
                    [[recordId]]
                );
                
                this.env.services.notification.add("Repaso iniciado", { 
                    type: "info" 
                });

                window.location.reload();
                
            } catch (error) {
                console.error("Error en iniciarRepaso:", error);
            }
        }
        
    });
}