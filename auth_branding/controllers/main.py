import hashlib
import json
import math
import re
from datetime import timezone
from email.utils import format_datetime
from urllib.parse import urlsplit

from markupsafe import Markup

from odoo import fields, http
from odoo.http import request

from ..models.auth_branding_config import AuthBrandingConfig


class AuthBrandingController(http.Controller):
    _ALLOWED_IMAGE_FIELDS = {"company_logo", "favicon", "background_image"}
    _ALLOWED_PAGES = {
        "login": "web.login",
        "signup": "auth_signup.signup",
        "reset": "auth_signup.reset_password",
    }
    _COLOR_DEFAULTS = {
        "primary_color": "#714B67",
        "secondary_color": "#FFFFFF",
        "background_color": "#F8F9FA",
        "gradient_start": "#714B67",
        "gradient_end": "#2B124C",
        "text_color": "#212529",
        "card_background_color": "#FFFFFF",
        "button_color": "#714B67",
        "button_text_color": "#FFFFFF",
    }
    _GRADIENT_DIRECTIONS = {
        "to right",
        "to bottom",
        "to bottom right",
        "to bottom left",
    }
    _BACKGROUND_TYPES = {"solid", "gradient", "animated_gradient", "image"}
    _TEMPLATES = {"centered", "split", "fullbleed", "minimal", "sidebar"}
    _SPLIT_ALIGNMENTS = {"left", "right"}
    _COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")

    @staticmethod
    def _safe_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _value(config, field_name, default=False):
        if isinstance(config, dict):
            return config.get(field_name, default)
        return getattr(config, field_name, default)

    @classmethod
    def _safe_color(cls, value, default):
        return value if value and cls._COLOR_PATTERN.fullmatch(str(value)) else default

    @staticmethod
    def _safe_number(value, default, minimum=0.0, maximum=None):
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = float(default)
        if not math.isfinite(number):
            number = float(default)
        number = max(minimum, number)
        if maximum is not None:
            number = min(maximum, number)
        return f"{number:g}"

    @staticmethod
    def _safe_selection(value, allowed, default):
        return value if value in allowed else default

    @staticmethod
    def _safe_url(value, default=""):
        if not value:
            return ""
        value = str(value)
        try:
            parsed = urlsplit(value)
        except ValueError:
            return default
        if (
            value != value.strip()
            or parsed.scheme.lower() not in {"http", "https"}
            or not parsed.netloc
        ):
            return default
        return value

    def _get_config(self, requested_company_id):
        return request.env["auth.branding.config"]._get_request_config(
            company_id=requested_company_id
        )

    def _normalized_css_values(self, config):
        values = {
            field_name: self._safe_color(
                self._value(config, field_name), default_value
            )
            for field_name, default_value in self._COLOR_DEFAULTS.items()
        }
        values.update(
            {
                "company_id": self._safe_int(
                    self._value(config, "company_id")
                    if isinstance(config, dict)
                    else config.company_id.id,
                    request.env.company.id,
                ),
                "background_type": self._safe_selection(
                    self._value(config, "background_type"),
                    self._BACKGROUND_TYPES,
                    "solid",
                ),
                "gradient_direction": self._safe_selection(
                    self._value(config, "gradient_direction"),
                    self._GRADIENT_DIRECTIONS,
                    "to bottom right",
                ),
                "font_family": self._safe_selection(
                    self._value(config, "font_family"),
                    set(AuthBrandingConfig.FONT_MAP),
                    "system-ui",
                ),
                "background_overlay_opacity": self._safe_number(
                    self._value(config, "background_overlay_opacity"),
                    0.3,
                    maximum=1.0,
                ),
                "glassmorphism_blur": self._safe_number(
                    self._value(config, "glassmorphism_blur"), 10
                ),
                "glassmorphism_opacity": self._safe_number(
                    self._value(config, "glassmorphism_opacity"),
                    0.2,
                    maximum=1.0,
                ),
                "input_border_radius": self._safe_number(
                    self._value(config, "input_border_radius"), 6
                ),
                "button_border_radius": self._safe_number(
                    self._value(config, "button_border_radius"), 6
                ),
            }
        )
        return values

    def _build_css_variables(self, config):
        values = self._normalized_css_values(config)
        font_family = AuthBrandingConfig.FONT_MAP[values["font_family"]]
        primary_rgb = ", ".join(
            str(int(values["primary_color"][offset : offset + 2], 16))
            for offset in (1, 3, 5)
        )
        return f""":root {{
    --ab-primary: {values['primary_color']};
    --ab-primary-rgb: {primary_rgb};
    --ab-secondary: {values['secondary_color']};
    --ab-overlay-opacity: {values['background_overlay_opacity']};
    --ab-font: {font_family};
    --ab-text-color: {values['text_color']};
    --ab-card-bg: {values['card_background_color']};
    --ab-glass-blur: {values['glassmorphism_blur']}px;
    --ab-glass-opacity: {values['glassmorphism_opacity']};
    --ab-input-radius: {values['input_border_radius']}px;
    --ab-btn-radius: {values['button_border_radius']}px;
    --ab-btn-color: {values['button_color']};
    --ab-btn-text: {values['button_text_color']};
}}"""

    def _build_background_css(self, config):
        values = self._normalized_css_values(config)
        if values["background_type"] == "solid":
            return f"background: {values['background_color']};"
        if values["background_type"] == "gradient":
            return (
                "background: linear-gradient("
                f"{values['gradient_direction']}, {values['gradient_start']}, "
                f"{values['gradient_end']});"
            )
        if values["background_type"] == "animated_gradient":
            return (
                "background: linear-gradient(-45deg, "
                f"{values['gradient_start']}, {values['gradient_end']}, "
                f"{values['primary_color']}); "
                "background-size: 400% 400%; "
                "animation: abGradientAnim 15s ease infinite;"
            )
        return (
            "background: url('/auth_branding/image/background_image?company_id="
            f"{values['company_id']}') no-repeat center center fixed; "
            "background-size: cover;"
        )

    def _build_theme_css(self, config):
        variables = self._build_css_variables(config)
        background = self._build_background_css(config)
        custom_css = AuthBrandingConfig._sanitize_custom_css(
            self._value(config, "custom_css", "")
        )
        custom_css_block = f"\n/* Custom CSS */\n{custom_css}" if custom_css else ""
        return f"""@keyframes abGradientAnim {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
{variables}

body.ab-template-centered, body.ab-template-minimal, body.ab-template-fullbleed {{
    {background}
}}
body.ab-template-split .ab-split-aside,
body.ab-template-sidebar .ab-split-aside {{
    {background}
}}
{custom_css_block}
"""

    @staticmethod
    def _boolean_parameter(kwargs, field_name, default):
        if field_name not in kwargs:
            return default
        return kwargs[field_name] == "true"

    def _build_preview_config(self, config, kwargs):
        color_values = {
            field_name: self._safe_color(
                kwargs.get(field_name, config[field_name]), default_value
            )
            for field_name, default_value in self._COLOR_DEFAULTS.items()
        }
        config_values = {
            "company_id": config.company_id.id,
            "company_logo": bool(config.company_logo),
            "favicon": bool(config.favicon),
            "template": self._safe_selection(
                kwargs.get("template", config.template),
                self._TEMPLATES,
                config.template,
            ),
            "split_alignment": self._safe_selection(
                kwargs.get("split_alignment", config.split_alignment),
                self._SPLIT_ALIGNMENTS,
                config.split_alignment or "left",
            ),
            "background_type": self._safe_selection(
                kwargs.get("background_type", config.background_type),
                self._BACKGROUND_TYPES,
                config.background_type,
            ),
            "gradient_direction": self._safe_selection(
                kwargs.get("gradient_direction", config.gradient_direction),
                self._GRADIENT_DIRECTIONS,
                config.gradient_direction or "to bottom right",
            ),
            "font_family": self._safe_selection(
                kwargs.get("font_family", config.font_family),
                set(AuthBrandingConfig.FONT_MAP),
                config.font_family,
            ),
            "background_overlay_opacity": self._safe_number(
                kwargs.get(
                    "background_overlay_opacity",
                    config.background_overlay_opacity,
                ),
                config.background_overlay_opacity,
                maximum=1.0,
            ),
            "glassmorphism_blur": self._safe_number(
                kwargs.get("glassmorphism_blur", config.glassmorphism_blur),
                config.glassmorphism_blur,
            ),
            "glassmorphism_opacity": self._safe_number(
                kwargs.get("glassmorphism_opacity", config.glassmorphism_opacity),
                config.glassmorphism_opacity,
                maximum=1.0,
            ),
            "input_border_radius": self._safe_number(
                kwargs.get("input_border_radius", config.input_border_radius),
                config.input_border_radius,
            ),
            "button_border_radius": self._safe_number(
                kwargs.get("button_border_radius", config.button_border_radius),
                config.button_border_radius,
            ),
            "glassmorphism": self._boolean_parameter(
                kwargs, "glassmorphism", config.glassmorphism
            ),
            "show_manage_databases": self._boolean_parameter(
                kwargs, "show_manage_databases", config.show_manage_databases
            ),
            "show_powered_by_odoo": self._boolean_parameter(
                kwargs, "show_powered_by_odoo", config.show_powered_by_odoo
            ),
            "tagline": kwargs.get("tagline", config.tagline or "")[:500],
            "custom_footer_text": kwargs.get(
                "custom_footer_text", config.custom_footer_text or ""
            )[:500],
            "login_welcome_title": kwargs.get(
                "login_welcome_title", config.login_welcome_title or ""
            )[:500],
            "login_welcome_subtitle": kwargs.get(
                "login_welcome_subtitle", config.login_welcome_subtitle or ""
            )[:500],
            "signup_welcome_title": kwargs.get(
                "signup_welcome_title", config.signup_welcome_title or ""
            )[:500],
            "signup_welcome_subtitle": kwargs.get(
                "signup_welcome_subtitle", config.signup_welcome_subtitle or ""
            )[:500],
            "reset_welcome_title": kwargs.get(
                "reset_welcome_title", config.reset_welcome_title or ""
            )[:500],
            "reset_welcome_subtitle": kwargs.get(
                "reset_welcome_subtitle", config.reset_welcome_subtitle or ""
            )[:500],
            "page_title": kwargs.get("page_title", config.page_title or "")[:200],
            "page_title_signup": kwargs.get(
                "page_title_signup", config.page_title_signup or ""
            )[:200],
            "page_title_reset": kwargs.get(
                "page_title_reset", config.page_title_reset or ""
            )[:200],
            "social_button_style": self._safe_selection(
                kwargs.get("social_button_style", config.social_button_style),
                {"rounded", "pill", "square", "icon"},
                "rounded",
            ),
            "hide_social_labels": self._boolean_parameter(
                kwargs, "hide_social_labels", config.hide_social_labels
            ),
            "dark_mode": self._safe_selection(
                kwargs.get("dark_mode", config.dark_mode),
                {"off", "auto", "on"},
                "off",
            ),
            "show_loading_animation": self._boolean_parameter(
                kwargs,
                "show_loading_animation",
                config.show_loading_animation,
            ),
            "loading_animation_type": self._safe_selection(
                kwargs.get(
                    "loading_animation_type", config.loading_animation_type
                ),
                {"spinner", "progress", "pulse"},
                "spinner",
            ),
            "powered_by_text": kwargs.get(
                "powered_by_text", config.powered_by_text or ""
            )[:200],
            "powered_by_url": self._safe_url(
                kwargs.get("powered_by_url", config.powered_by_url or "")
            ),
            "custom_css": AuthBrandingConfig._sanitize_custom_css(config.custom_css),
            "terms_url": self._safe_url(
                kwargs.get("terms_url", config.terms_url or "")
            ),
            "privacy_url": self._safe_url(
                kwargs.get("privacy_url", config.privacy_url or "")
            ),
            "terms_label": kwargs.get(
                "terms_label", config.terms_label or "Terms of Service"
            )[:200],
            "privacy_label": kwargs.get(
                "privacy_label", config.privacy_label or "Privacy Policy"
            )[:200],
            "is_preview": True,
        }
        config_values.update(color_values)

        get_param = request.env["ir.config_parameter"].sudo().get_param
        config_values["auth_signup_uninvited"] = get_param(
            "auth_signup.invitation_scope", "b2b"
        )
        config_values["auth_signup_reset_password"] = (
            get_param("auth_signup.reset_password", "False").lower() == "true"
        )
        config_values["inline_style"] = Markup(
            self._build_theme_css(config_values)
        )
        return config_values

    @staticmethod
    def _cache_headers(config, variant):
        modified = config.write_date or config.create_date or fields.Datetime.now()
        if modified.tzinfo is None:
            modified = modified.replace(tzinfo=timezone.utc)
        modified = modified.replace(microsecond=0)
        identity = f"{config._name}:{config.id}:{config.write_date}:{variant}".encode()
        etag = hashlib.sha256(identity).hexdigest()
        return etag, modified, [
            ("ETag", f'"{etag}"'),
            ("Last-Modified", format_datetime(modified, usegmt=True)),
            ("Cache-Control", "public, max-age=3600, must-revalidate"),
            ("X-Content-Type-Options", "nosniff"),
        ]

    @staticmethod
    def _is_not_modified(etag, modified):
        if request.httprequest.if_none_match:
            return request.httprequest.if_none_match.contains(etag)
        if_modified_since = request.httprequest.if_modified_since
        return bool(if_modified_since and modified <= if_modified_since)

    @http.route(
        "/auth_branding/preview",
        type="http",
        auth="user",
        website=True,
        sitemap=False,
    )
    def preview(self, page="login", **kwargs):
        config = self._get_config(kwargs.get("company_id"))
        ab_config = self._build_preview_config(config, kwargs)
        page = page if page in self._ALLOWED_PAGES else "login"
        ab_config["page"] = page
        if page == "signup":
            ab_config["login_welcome_title"] = ab_config["signup_welcome_title"]
            ab_config["login_welcome_subtitle"] = ab_config[
                "signup_welcome_subtitle"
            ]
        elif page == "reset":
            ab_config["login_welcome_title"] = ab_config["reset_welcome_title"]
            ab_config["login_welcome_subtitle"] = ab_config[
                "reset_welcome_subtitle"
            ]
        request.update_context(ab_preview_config=ab_config)

        qcontext = {
            "error": False,
            "message": False,
            "login": "admin",
            "redirect": "",
            "providers": [],
            "signup_enabled": ab_config["auth_signup_uninvited"] == "b2c",
            "reset_password_enabled": ab_config["auth_signup_reset_password"],
            "token": False,
        }
        template = self._ALLOWED_PAGES.get(page, self._ALLOWED_PAGES["login"])
        response = request.render(template, qcontext)
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response

    @http.route(
        "/auth_branding/theme.css",
        type="http",
        auth="public",
        sitemap=False,
    )
    def theme_css(self, **kwargs):
        config = self._get_config(kwargs.get("company_id"))
        published_resource = config._get_published_resource()
        etag, modified, headers = self._cache_headers(
            published_resource, "theme.css"
        )
        headers.append(("Content-Type", "text/css; charset=utf-8"))
        if self._is_not_modified(etag, modified):
            return request.make_response("", headers=headers, status=304)
        return request.make_response(
            self._build_theme_css(config._get_frontend_values()), headers=headers
        )

    @http.route(
        "/auth_branding/image/<string:field>",
        type="http",
        auth="public",
        sitemap=False,
    )
    def get_image(self, field, **kwargs):
        if field not in self._ALLOWED_IMAGE_FIELDS:
            return request.not_found()

        config = self._get_config(kwargs.get("company_id"))
        published_resource = config._get_published_resource()
        if not published_resource[field]:
            return request.not_found()

        etag, modified, headers = self._cache_headers(published_resource, field)
        headers.extend(
            [
                ("Content-Security-Policy", "default-src 'none'; sandbox"),
                ("Cross-Origin-Resource-Policy", "same-origin"),
            ]
        )
        if self._is_not_modified(etag, modified):
            return request.make_response("", headers=headers, status=304)

        response = request.env["ir.binary"]._get_stream_from(
            published_resource, field
        ).get_response()
        for header, value in headers:
            response.headers[header] = value
        return response

    @http.route(
        "/auth_branding/export/<int:config_id>",
        type="http",
        auth="user",
        sitemap=False,
    )
    def export_branding(self, config_id):
        config = request.env["auth.branding.config"].browse(config_id).exists()
        if not config:
            return request.not_found()
        config.check_access("read")
        payload = json.dumps(
            config._get_export_payload(), indent=2, sort_keys=True
        ).encode("utf-8")
        company_slug = re.sub(
            r"[^a-z0-9]+", "-", config.company_id.display_name.lower()
        ).strip("-") or "company"
        return request.make_response(
            payload,
            headers=[
                ("Content-Type", "application/json; charset=utf-8"),
                (
                    "Content-Disposition",
                    f'attachment; filename="auth-branding-{company_slug}.json"',
                ),
                ("Cache-Control", "private, no-store"),
                ("X-Content-Type-Options", "nosniff"),
            ],
        )
