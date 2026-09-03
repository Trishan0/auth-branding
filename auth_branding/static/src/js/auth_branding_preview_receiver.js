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
const TEXT_FALLBACKS = {
    terms_label: "Terms of Service",
    privacy_label: "Privacy Policy",
    powered_by_text: "Powered by Odoo",
};
let loaderHideTimeout;
let lastLoaderSignature;
const UNSAFE_CSS_PATTERN = /[<>\\]|@(?:import|charset|namespace)\b|expression\s*\(|url\s*\(|(?:https?|ftp|file|blob)\s*:|\/\/|(?:java|vb)script\s*:|data\s*:|-moz-binding\b|behavior\s*:/i;

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

function updateLoaderPreview(visible) {
    window.clearTimeout(loaderHideTimeout);
    for (const loader of document.querySelectorAll(".ab-page-loader")) {
        loader.classList.toggle("d-none", !visible);
        loader.classList.toggle("is-hidden", !visible);
    }
    if (visible) {
        loaderHideTimeout = window.setTimeout(() => {
            for (const loader of document.querySelectorAll(".ab-page-loader")) {
                loader.classList.add("is-hidden");
            }
        }, 650);
    }
}

function updateCustomCss(value) {
    const css = typeof value === "string" ? value : "";
    const cssWithoutComments = css.replace(/\/\*[\s\S]*?\*\//g, "");
    const hasUnclosedComment = (css.match(/\/\*/g) || []).length !==
        (css.match(/\*\//g) || []).length;
    let style = document.getElementById("ab-custom-css-preview");
    if (!style) {
        style = document.createElement("style");
        style.id = "ab-custom-css-preview";
        document.body.appendChild(style);
    }
    style.textContent = css.length <= 50000 &&
        !hasUnclosedComment &&
        !UNSAFE_CSS_PATTERN.test(cssWithoutComments) ? css : "";
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
        const previewMode = document.querySelector(
            "[data-auth-branding-preview]"
        )?.dataset.previewMode;
        const imageRoute = previewMode === "draft"
            ? "/auth_branding/preview/image/"
            : "/auth_branding/image/";
        background = `url('${imageRoute}background_image?company_id=${companyId}') center / cover no-repeat fixed`;
    }

    let liveTheme = document.getElementById("ab-live-theme-preview");
    if (!liveTheme) {
        liveTheme = document.createElement("style");
        liveTheme.id = "ab-live-theme-preview";
        document.body.appendChild(liveTheme);
    }
    const backgroundSize = type === "animated_gradient" ? "400% 400%" : "cover";
    const animation = type === "animated_gradient"
        ? "abGradientAnim 15s ease infinite"
        : "none";
    liveTheme.textContent = `
body.ab-template-centered,
body.ab-template-minimal,
body.ab-template-fullbleed {
    background: ${background};
    background-size: ${backgroundSize};
    animation: ${animation};
}
body.ab-template-split .ab-split-aside,
body.ab-template-sidebar .ab-split-aside {
    background: ${background};
    background-size: ${backgroundSize};
    animation: ${animation};
}`;
    document.body.classList.toggle("ab-bg-animated", type === "animated_gradient");
    document.body.classList.toggle("ab-bg-image", type === "image");
}

function applyUpdate(values) {
    const root = document.documentElement;
    for (const [field, variable] of Object.entries(COLOR_VARIABLES)) {
        if (COLOR_PATTERN.test(values[field])) {
            root.style.setProperty(variable, values[field]);
            if (field === "primary_color") {
                const rgb = [1, 3, 5]
                    .map((offset) => parseInt(values[field].slice(offset, offset + 2), 16))
                    .join(", ");
                root.style.setProperty("--ab-primary-rgb", rgb);
            }
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

    if (typeof values.glassmorphism === "boolean") {
        document.body.classList.toggle("ab-glass", values.glassmorphism);
    }
    if (["left", "right"].includes(values.split_alignment)) {
        document.body.classList.toggle(
            "ab-split-right",
            values.split_alignment === "right"
        );
    }
    const darkModes = ["off", "auto", "on"];
    if (darkModes.includes(values.dark_mode)) {
        for (const mode of darkModes) {
            document.body.classList.toggle(`ab-dark-${mode}`, values.dark_mode === mode);
        }
    }
    const socialStyles = ["rounded", "pill", "square", "icon"];
    if (socialStyles.includes(values.social_button_style)) {
        for (const style of socialStyles) {
            document.body.classList.toggle(
                `ab-social-${style}`,
                values.social_button_style === style
            );
        }
    }
    if (typeof values.hide_social_labels === "boolean") {
        document.body.classList.toggle(
            "ab-social-hide-labels",
            values.hide_social_labels
        );
    }
    const loadingTypes = ["spinner", "progress", "pulse"];
    if (loadingTypes.includes(values.loading_animation_type)) {
        for (const loader of document.querySelectorAll(".ab-page-loader")) {
            for (const type of loadingTypes) {
                loader.classList.toggle(
                    `ab-loading-${type}`,
                    values.loading_animation_type === type
                );
            }
        }
    }
    updateBackground(values);

    for (const field of [
        "tagline",
        "login_welcome_title",
        "login_welcome_subtitle",
        "custom_footer_text",
        "terms_label",
        "privacy_label",
        "powered_by_text",
    ]) {
        if (values[field] !== undefined) {
            setText(field, values[field] || TEXT_FALLBACKS[field] || "");
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
    if (values.terms_url !== undefined) {
        setExternalLink("terms_url", values.terms_url);
    }
    if (values.privacy_url !== undefined) {
        setExternalLink("privacy_url", values.privacy_url);
    }
    if (values.powered_by_url !== undefined) {
        setExternalLink(
            "powered_by_url",
            values.powered_by_url || "https://www.odoo.com"
        );
    }
    if (typeof values.show_manage_databases === "boolean") {
        setVisibility("show_manage_databases", values.show_manage_databases);
    }
    if (typeof values.show_powered_by_odoo === "boolean") {
        setVisibility("show_powered_by_odoo", values.show_powered_by_odoo);
    }
    if (typeof values.show_loading_animation === "boolean") {
        const loaderSignature = `${values.show_loading_animation}:${values.loading_animation_type}`;
        if (loaderSignature !== lastLoaderSignature) {
            lastLoaderSignature = loaderSignature;
            updateLoaderPreview(values.show_loading_animation);
        }
    }
    if (values.custom_css !== undefined) {
        updateCustomCss(values.custom_css);
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
