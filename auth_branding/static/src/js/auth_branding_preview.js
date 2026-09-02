/** @odoo-module **/

import { registry } from "@web/core/registry";
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
                'company_id', 'template', 'tagline', 'primary_color', 'secondary_color',
                'background_type', 'background_color', 'gradient_start', 
                'gradient_end', 'gradient_direction', 'background_overlay_opacity',
                'font_family', 'text_color', 'input_border_radius', 
                'button_border_radius', 'button_color', 'button_text_color',
                'show_manage_databases', 'show_powered_by_odoo',
                'split_alignment', 'card_background_color', 'glassmorphism', 'glassmorphism_blur', 'glassmorphism_opacity',
                'custom_footer_text', 'login_welcome_title', 'login_welcome_subtitle',
                'terms_url', 'privacy_url', 'terms_label', 'privacy_label',
            ];
            
            // Boolean fields need special handling — send 'true'/'false' as strings
            const boolFields = new Set(['show_manage_databases', 'show_powered_by_odoo', 'glassmorphism']);
            for (const f of fieldsToWatch) {
                let val = data[f];
                // Extract ID from Many2one (which can be [id, name] or an object {id: 123, ...})
                if (Array.isArray(val)) {
                    val = val[0];
                } else if (val && typeof val === 'object' && val.id) {
                    val = val.id;
                }

                if (boolFields.has(f)) {
                    params.append(f, val ? 'true' : 'false');
                } else if (val !== undefined && val !== false && val !== '') {
                    params.append(f, val);
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
                data.company_id,
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
                data.show_manage_databases,
                data.show_powered_by_odoo,
                data.split_alignment,
                data.card_background_color,
                data.glassmorphism,
                data.glassmorphism_blur,
                data.glassmorphism_opacity,
                data.custom_footer_text,
                data.login_welcome_title,
                data.login_welcome_subtitle,
                data.terms_url,
                data.privacy_url,
                data.terms_label,
                data.privacy_label,
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
