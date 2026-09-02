/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useService } from "@web/core/utils/hooks";


export class AuthBrandingPresetGallery extends Component {
    static template = "auth_branding.PresetGallery";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.state = useState({
            loading: true,
            applyingId: null,
            selectedId: null,
            presets: [],
        });

        onWillStart(async () => {
            const fields = await this.orm.call(
                "auth.branding.preset",
                "get_editor_fields",
                []
            );
            this.state.presets = await this.orm.searchRead(
                "auth.branding.preset",
                [["active", "=", true]],
                fields,
                { order: "sequence, name, id" }
            );
            this.state.loading = false;
        });
    }

    getBackgroundStyle(preset) {
        if (preset.background_type === "solid") {
            return `background: ${preset.background_color}`;
        }
        return `background: linear-gradient(135deg, ${preset.gradient_start}, ${preset.gradient_end})`;
    }

    async applyPreset(preset) {
        this.state.applyingId = preset.id;
        try {
            const values = await this.orm.call(
                "auth.branding.preset",
                "get_values_for_editor",
                [[preset.id]]
            );
            await this.props.record.update(values);
            this.state.selectedId = preset.id;
            this.notification.add(`${preset.name} applied to the preview.`, {
                title: "Theme applied",
                type: "success",
            });
        } finally {
            this.state.applyingId = null;
        }
    }

    deletePreset(preset) {
        this.dialog.add(ConfirmationDialog, {
            title: "Delete custom theme?",
            body: `${preset.name} will be permanently removed. Your current draft is not changed.`,
            confirmLabel: "Delete Theme",
            confirm: async () => {
                await this.orm.unlink("auth.branding.preset", [preset.id]);
                this.state.presets = this.state.presets.filter(
                    (item) => item.id !== preset.id
                );
                if (this.state.selectedId === preset.id) {
                    this.state.selectedId = null;
                }
                this.notification.add(`${preset.name} deleted.`, {
                    title: "Theme deleted",
                    type: "success",
                });
            },
        });
    }
}

registry.category("view_widgets").add("auth_branding_preset_gallery", {
    component: AuthBrandingPresetGallery,
});
