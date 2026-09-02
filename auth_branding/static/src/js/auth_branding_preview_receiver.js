/** @odoo-module **/

const COLOR_PATTERN = /^#[0-9A-Fa-f]{6}$/;
const FONT_MAP = {
    "system-ui": 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    Inter: '"Inter", sans-serif',
    Roboto: '"Roboto", sans-serif',
    "Open Sans": '"Open Sans", sans-serif',
    Lato: '"Lato", sans-serif',
    Poppins: '"Poppins", sans-serif',
    Georgia: "Georgia, serif",
};
const COLOR_VARIABLES = {
    primary_color: "--ab-primary",
    secondary_color: "--ab-secondary",
    text_color: "--ab-text-color",
    card_background_color: "--ab-card-bg",
    button_color: "--ab-btn-color",
    button_text_color: "--ab-btn-text",
};
const NUMBER_VARIABLES = {
    background_overlay_opacity: ["--ab-overlay-opacity", 0, 1, ""],
    glassmorphism_blur: ["--ab-glass-blur", 0, 100, "px"],
    glassmorphism_opacity: ["--ab-glass-opacity", 0, 1, ""],
    input_border_radius: ["--ab-input-radius", 0, 100, "px"],
    button_border_radius: ["--ab-btn-radius", 0, 100, "px"],
};

function safeNumber(value, minimum, maximum) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
        return null;
    }
    return Math.min(maximum, Math.max(minimum, parsed));
}

function setText(name, value) {
    const text = typeof value === "string" ? value.slice(0, 500) : "";
    for (const element of document.querySelectorAll(`[data-ab-text="${name}"]`)) {
        element.textContent = text;
        element.classList.toggle("d-none", !text);
    }
}

function setVisibility(name, visible) {
    for (const element of document.querySelectorAll(`[data-ab-visible="${name}"]`)) {
        element.classList.toggle("d-none", !visible);
    }
}

function setExternalLink(name, value) {
    let safeUrl = "";
    if (typeof value === "string" && value) {
        try {
            const parsed = new URL(value);
            if (["http:", "https:"].includes(parsed.protocol)) {
                safeUrl = parsed.href;
            }
        } catch {
            safeUrl = "";
        }
    }
    for (const element of document.querySelectorAll(`[data-ab-link="${name}"]`)) {
        element.href = safeUrl || "#";
        element.classList.toggle("d-none", !safeUrl);
    }
}

function updateBackground(values) {
    const type = ["solid", "gradient", "animated_gradient", "image"].includes(
        values.background_type
    )
        ? values.background_type
        : "solid";
    const color = COLOR_PATTERN.test(values.background_color)
        ? values.background_color
        : "#F8F9FA";
    const start = COLOR_PATTERN.test(values.gradient_start)
        ? values.gradient_start
        : "#714B67";
    const end = COLOR_PATTERN.test(values.gradient_end)
        ? values.gradient_end
        : "#2B124C";
    const primary = COLOR_PATTERN.test(values.primary_color)
        ? values.primary_color
        : "#714B67";
    const directions = ["to right", "to bottom", "to bottom right", "to bottom left"];
    const direction = directions.includes(values.gradient_direction)
        ? values.gradient_direction
        : "to bottom right";
    const companyId = Number.isInteger(Number(values.company_id))
        ? Number(values.company_id)
        : 0;

    let background;
    if (type === "solid") {
        background = color;
    } else if (type === "gradient") {
        background = `linear-gradient(${direction}, ${start}, ${end})`;
    } else if (type === "animated_gradient") {
        background = `linear-gradient(-45deg, ${start}, ${end}, ${primary})`;
    } else {
        background = `url('/auth_branding/image/background_image?company_id=${companyId}') center / cover no-repeat fixed`;
    }

    const targets = document.querySelectorAll(
        "body.ab-template-centered, body.ab-template-fullbleed, body.ab-template-split .ab-split-aside"
    );
    for (const target of targets) {
        target.style.setProperty("background", background, "important");
        target.style.setProperty(
            "background-size",
            type === "animated_gradient" ? "400% 400%" : "cover",
            "important"
        );
        target.style.setProperty(
            "animation",
            type === "animated_gradient" ? "abGradientAnim 15s ease infinite" : "none",
            "important"
        );
    }
    document.body.classList.toggle("ab-bg-animated", type === "animated_gradient");
}

function applyUpdate(values) {
    const root = document.documentElement;
    for (const [field, variable] of Object.entries(COLOR_VARIABLES)) {
        if (COLOR_PATTERN.test(values[field])) {
            root.style.setProperty(variable, values[field]);
        }
    }
    for (const [field, [variable, minimum, maximum, unit]] of Object.entries(
        NUMBER_VARIABLES
    )) {
        const number = safeNumber(values[field], minimum, maximum);
        if (number !== null) {
            root.style.setProperty(variable, `${number}${unit}`);
            if (field === "background_overlay_opacity") {
                for (const overlay of document.querySelectorAll(".ab-background-overlay")) {
                    overlay.style.opacity = number;
                }
            }
        }
    }
    if (FONT_MAP[values.font_family]) {
        root.style.setProperty("--ab-font", FONT_MAP[values.font_family]);
    }

    document.body.classList.toggle("ab-glass", values.glassmorphism === true);
    document.body.classList.toggle(
        "ab-split-right",
        values.split_alignment === "right"
    );
    updateBackground(values);

    for (const field of [
        "tagline",
        "login_welcome_title",
        "login_welcome_subtitle",
        "custom_footer_text",
        "terms_label",
        "privacy_label",
    ]) {
        if (values[field] !== undefined) {
            setText(field, values[field]);
        }
    }
    if (
        values.login_welcome_title !== undefined ||
        values.login_welcome_subtitle !== undefined
    ) {
        for (const block of document.querySelectorAll(".ab-welcome-block")) {
            const hasVisibleContent = [...block.querySelectorAll("[data-ab-text]")].some(
                (element) => !element.classList.contains("d-none")
            );
            block.classList.toggle("d-none", !hasVisibleContent);
        }
    }
    if (typeof values.show_manage_databases === "boolean") {
        setVisibility("show_manage_databases", values.show_manage_databases);
    }
    if (typeof values.show_powered_by_odoo === "boolean") {
        setVisibility("show_powered_by_odoo", values.show_powered_by_odoo);
    }
    if (values.terms_url !== undefined) {
        setExternalLink("terms_url", values.terms_url);
    }
    if (values.privacy_url !== undefined) {
        setExternalLink("privacy_url", values.privacy_url);
    }
}

window.addEventListener("message", (event) => {
    if (
        event.origin !== window.location.origin ||
        event.source !== window.parent ||
        !document.querySelector("[data-auth-branding-preview]") ||
        event.data?.type !== "auth_branding:update" ||
        !event.data.values ||
        typeof event.data.values !== "object"
    ) {
        return;
    }
    applyUpdate(event.data.values);
});
