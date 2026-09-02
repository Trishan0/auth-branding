/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";


function rgbFromHex(value, fallback) {
    const color = /^#[0-9a-f]{6}$/i.test(value || "") ? value : fallback;
    return [1, 3, 5].map((offset) => parseInt(color.slice(offset, offset + 2), 16));
}

function luminance(color) {
    const channels = rgbFromHex(color, "#000000").map((channel) => {
        const value = channel / 255;
        return value <= 0.04045
            ? value / 12.92
            : ((value + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
}

function contrastRatio(first, second) {
    const lighter = Math.max(luminance(first), luminance(second));
    const darker = Math.min(luminance(first), luminance(second));
    return (lighter + 0.05) / (darker + 0.05);
}

export class AuthBrandingAccessibility extends Component {
    static template = "auth_branding.AccessibilityChecks";
    static props = ["*"];

    get checks() {
        const values = this.props.record.data;
        const lightSurface = {
            card: values.card_background_color || "#FFFFFF",
            text: values.text_color || "#212529",
        };
        const darkSurface = { card: "#111827", text: "#E5E7EB" };
        const surfaces = values.dark_mode === "on"
            ? [darkSurface]
            : values.dark_mode === "auto"
              ? [lightSurface, darkSurface]
              : [lightSurface];
        const lowestText = Math.min(
            ...surfaces.map((surface) => contrastRatio(surface.text, surface.card))
        );
        const lowestLink = Math.min(
            ...surfaces.map((surface) =>
                contrastRatio(values.primary_color || "#714B67", surface.card)
            )
        );
        const button = contrastRatio(
            values.button_text_color || "#FFFFFF",
            values.button_color || "#714B67"
        );
        return [
            {
                key: "text",
                label: "Body text contrast",
                ratio: lowestText,
                pass: lowestText >= 4.5,
                hint: "Text and card background should reach 4.5:1.",
            },
            {
                key: "button",
                label: "Button label contrast",
                ratio: button,
                pass: button >= 4.5,
                hint: "Button text and button color should reach 4.5:1.",
            },
            {
                key: "link",
                label: "Link color contrast",
                ratio: lowestLink,
                pass: lowestLink >= 4.5,
                hint: "Primary-color links should reach 4.5:1 on the card.",
            },
        ];
    }

    get passedCount() {
        return this.checks.filter((check) => check.pass).length;
    }

    formatRatio(ratio) {
        return `${ratio.toFixed(2)}:1`;
    }
}

registry.category("view_widgets").add("auth_branding_accessibility", {
    component: AuthBrandingAccessibility,
});
