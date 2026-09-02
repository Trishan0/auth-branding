/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillUnmount, useEffect, useRef, useState } from "@odoo/owl";
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
        if (this.props.readonly) {
            return;
        }
        const val = ev.target.value;
        this.state.color = val;
        this.props.record.update({ [this.props.name]: val });
    }

    onTextInput(ev) {
        if (this.props.readonly) {
            return;
        }
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
        if (this.props.readonly) {
            return;
        }
        this.props.record.update({ [this.props.name]: templateName });
    }
}
registry.category("fields").add("auth_branding_template_picker", {
    component: AuthBrandingTemplatePicker,
});


const PREVIEW_FIELDS = [
    "company_id", "template", "tagline", "primary_color", "secondary_color",
    "background_type", "background_color", "gradient_start", "gradient_end",
    "gradient_direction", "background_overlay_opacity", "font_family", "text_color",
    "input_border_radius", "button_border_radius", "button_color", "button_text_color",
    "show_manage_databases", "show_powered_by_odoo", "split_alignment",
    "card_background_color", "glassmorphism", "glassmorphism_blur",
    "glassmorphism_opacity", "custom_footer_text", "login_welcome_title",
    "login_welcome_subtitle", "signup_welcome_title", "signup_welcome_subtitle",
    "reset_welcome_title", "reset_welcome_subtitle", "page_title", "page_title_signup",
    "page_title_reset", "social_button_style", "hide_social_labels", "terms_url",
    "privacy_url", "terms_label", "privacy_label",
    "dark_mode", "show_loading_animation", "loading_animation_type",
    "powered_by_text", "powered_by_url",
    "custom_css",
];
const URL_EXCLUDED_FIELDS = new Set(["custom_css"]);
const BOOLEAN_FIELDS = new Set([
    "show_manage_databases",
    "show_powered_by_odoo",
    "glassmorphism",
    "hide_social_labels",
    "show_loading_animation",
]);


// 3. Preview Widget
export class AuthBrandingPreview extends Component {
    static template = "auth_branding.PreviewWidget";
    static props = ["*"];

    setup() {
        this.state = useState({
            page: "login",
            device: "desktop",
            iframeSrc: "",
            ready: false,
        });
        this.previewFrame = useRef("previewFrame");
        this.reloadTimeout = null;

        useEffect(() => {
            const data = this.props.record.data;
            const newSrc = this.buildPreviewUrl(data);
            this.state.ready = false;
            clearTimeout(this.reloadTimeout);
            this.reloadTimeout = setTimeout(() => {
                this.state.iframeSrc = newSrc;
            }, 120);
        }, () => {
            const data = this.props.record.data;
            return [
                this.state.page,
                this.extractValue(data.company_id),
                data.template,
            ];
        });

        useEffect(() => {
            this.sendPreviewUpdate();
        }, () => [
            this.state.iframeSrc,
            ...PREVIEW_FIELDS.map((fieldName) =>
                this.extractValue(this.props.record.data[fieldName])
            ),
        ]);

        onWillUnmount(() => clearTimeout(this.reloadTimeout));
    }

    extractValue(value) {
        if (Array.isArray(value)) {
            return value[0];
        }
        if (value && typeof value === "object" && value.id) {
            return value.id;
        }
        return value;
    }

    getPreviewValues() {
        const data = this.props.record.data;
        const values = Object.fromEntries(
            PREVIEW_FIELDS.map((fieldName) => [
                fieldName,
                this.extractValue(data[fieldName]),
            ])
        );
        if (this.state.page === "signup") {
            values.login_welcome_title = values.signup_welcome_title;
            values.login_welcome_subtitle = values.signup_welcome_subtitle;
        } else if (this.state.page === "reset") {
            values.login_welcome_title = values.reset_welcome_title;
            values.login_welcome_subtitle = values.reset_welcome_subtitle;
        }
        return values;
    }

    buildPreviewUrl(data) {
        const params = new URLSearchParams({ page: this.state.page });
        for (const fieldName of PREVIEW_FIELDS) {
            if (URL_EXCLUDED_FIELDS.has(fieldName)) {
                continue;
            }
            const value = this.extractValue(data[fieldName]);
            if (BOOLEAN_FIELDS.has(fieldName) && value !== undefined) {
                params.append(fieldName, value ? "true" : "false");
            } else if (value !== undefined && value !== false && value !== "") {
                params.append(fieldName, value);
            }
        }
        return `/auth_branding/preview?${params.toString()}`;
    }

    sendPreviewUpdate() {
        const frameWindow = this.previewFrame.el?.contentWindow;
        if (!frameWindow) {
            return;
        }
        frameWindow.postMessage(
            { type: "auth_branding:update", values: this.getPreviewValues() },
            window.location.origin
        );
    }

    onIframeLoad() {
        this.state.ready = true;
        this.sendPreviewUpdate();
    }

    setPage(page) {
        this.state.page = page;
    }

    setDevice(device) {
        this.state.device = device;
    }
}

registry.category("view_widgets").add("auth_branding_preview", {
    component: AuthBrandingPreview,
});
