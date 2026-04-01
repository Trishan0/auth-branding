/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, useEffect } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

// 1. Color Field Component
export class AuthBrandingColorField extends Component {
    static template = "auth_branding.ColorField";
    static props = { ...standardFieldProps };

    setup() {
        this.state = useState({
            color: this.props.record.data[this.props.name] || "#000000",
        });
    }

    get color() {
        return this.props.record.data[this.props.name] || "#000000";
    }

    onColorInput(ev) {
        const val = ev.target.value;
        this.state.color = val;
        this.props.record.update({ [this.props.name]: val });
    }

    onTextInput(ev) {
        const val = ev.target.value;
        this.state.color = val;
        if (/^#[0-9A-F]{6}$/i.test(val)) {
            this.props.record.update({ [this.props.name]: val });
        }
    }
}
registry.category("fields").add("auth_branding_color", {
    component: AuthBrandingColorField,
});

// 2. Template Picker Field Component
export class AuthBrandingTemplatePicker extends Component {
    static template = "auth_branding.TemplatePicker";
    static props = { ...standardFieldProps };

    get selected() {
        return this.props.record.data[this.props.name];
    }

    selectTemplate(templateName) {
        this.props.record.update({ [this.props.name]: templateName });
    }
}
registry.category("fields").add("auth_branding_template_picker", {
    component: AuthBrandingTemplatePicker,
});


// 3. Preview Widget
export class AuthBrandingPreview extends Component {
    static template = "auth_branding.PreviewWidget";
    static props = ["*"];

    setup() {
        this.state = useState({
            page: "login",
            iframeSrc: "",
        });
        
        this.debounceTimeout = null;

        useEffect(() => {
            const data = this.props.record.data;
            const params = new URLSearchParams();
            params.append('page', this.state.page);
            
            const fieldsToWatch = [
                'template', 'tagline', 'primary_color', 'secondary_color',
                'background_type', 'background_color', 'gradient_start', 
                'gradient_end', 'gradient_direction', 'background_overlay_opacity',
                'font_family', 'text_color', 'input_border_radius', 
                'button_border_radius', 'button_color', 'button_text_color',
                'show_manage_databases', 'show_powered_by_odoo'
            ];
            
            for (const f of fieldsToWatch) {
                if (data[f] !== undefined && data[f] !== false) {
                    params.append(f, data[f]);
                }
            }

            const newSrc = `/auth_branding/preview?${params.toString()}`;
            
            clearTimeout(this.debounceTimeout);
            this.debounceTimeout = setTimeout(() => {
                this.state.iframeSrc = newSrc;
            }, 200);

        }, () => {
            const data = this.props.record.data;
            return [
                this.state.page,
                data.template,
                data.tagline,
                data.primary_color,
                data.secondary_color,
                data.background_type,
                data.background_color,
                data.gradient_start,
                data.gradient_end,
                data.gradient_direction,
                data.background_overlay_opacity,
                data.font_family,
                data.text_color,
                data.input_border_radius,
                data.button_border_radius,
                data.button_color,
                data.button_text_color,
            ];
        });
    }

    setPage(page) {
        this.state.page = page;
    }
}

registry.category("view_widgets").add("auth_branding_preview", {
    component: AuthBrandingPreview,
});
