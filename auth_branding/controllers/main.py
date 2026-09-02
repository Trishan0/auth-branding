import hashlib
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
    _TEMPLATES = {"centered", "split", "fullbleed"}
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
        return f""":root {{
    --ab-primary: {values['primary_color']};
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
            return f"background: {values['background_color']} !important;"
        if values["background_type"] == "gradient":
            return (
                "background: linear-gradient("
                f"{values['gradient_direction']}, {values['gradient_start']}, "
                f"{values['gradient_end']}) !important;"
            )
        if values["background_type"] == "animated_gradient":
            return (
                "background: linear-gradient(-45deg, "
                f"{values['gradient_start']}, {values['gradient_end']}, "
                f"{values['primary_color']}) !important; "
                "background-size: 400% 400% !important; "
                "animation: abGradientAnim 15s ease infinite !important;"
            )
        return (
            "background: url('/auth_branding/image/background_image?company_id="
            f"{values['company_id']}') no-repeat center center fixed !important; "
            "background-size: cover !important;"
        )

    def _build_theme_css(self, config):
        variables = self._build_css_variables(config)
        background = self._build_background_css(config)
        return f"""@keyframes abGradientAnim {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
{variables}

body.ab-template-centered, body.ab-template-fullbleed {{
    {background}
}}
body.ab-template-split .ab-split-aside {{
    {background}
}}
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
        identity = f"{config.id}:{config.write_date}:{variant}".encode()
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
        etag, modified, headers = self._cache_headers(config, "theme.css")
        headers.append(("Content-Type", "text/css; charset=utf-8"))
        if self._is_not_modified(etag, modified):
            return request.make_response("", headers=headers, status=304)
        return request.make_response(
            self._build_theme_css(config), headers=headers
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
        if not config[field]:
            return request.not_found()

        etag, modified, headers = self._cache_headers(config, field)
        headers.extend(
            [
                ("Content-Security-Policy", "default-src 'none'; sandbox"),
                ("Cross-Origin-Resource-Policy", "same-origin"),
            ]
        )
        if self._is_not_modified(etag, modified):
            return request.make_response("", headers=headers, status=304)

        response = request.env["ir.binary"]._get_stream_from(
            config, field
        ).get_response()
        for header, value in headers:
            response.headers[header] = value
        return response
