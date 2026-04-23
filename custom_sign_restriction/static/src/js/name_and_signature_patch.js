/** @odoo-module **/

import { NameAndSignature } from "@web/core/signature/name_and_signature";
import { patch } from "@web/core/utils/patch";

patch(NameAndSignature.prototype, {
    setup() {
        super.setup(...arguments);

        this.state.signMode = "draw";
        
        this.state.showSignatureArea = true;

        if (this.signaturePad) {
            this.signaturePad.on();
        }
    },

    setMode(mode, reset) {
        if (mode === 'auto') {
            return super.setMode('draw', reset);
        }
        return super.setMode(mode, reset);
    }
});