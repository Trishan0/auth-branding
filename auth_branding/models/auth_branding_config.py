import re
import warnings
from urllib.parse import urlsplit

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AuthBrandingConfig(models.Model):
    _name = "auth.branding.config"
    _description = "Authentication Branding Configuration"
    _rec_name = "company_id"
    _order = "company_id"

    COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")
    CUSTOM_CSS_MAX_LENGTH = 50000
    EXPORT_FORMAT = "odoo_auth_branding"
    EXPORT_SCHEMA_VERSION = 1
    UNSAFE_CSS_PATTERN = re.compile(
        r"(?:[<>\\]|@(?:import|charset|namespace)\b|expression\s*\(|"
        r"url\s*\(|(?:https?|ftp|file|blob)\s*:|//|(?:java|vb)script\s*:|data\s*:|"
        r"-moz-binding\b|behavior\s*:)",
        re.IGNORECASE,
    )
    COLOR_FIELDS = (
        "card_background_color",
        "primary_color",
        "secondary_color",
        "background_color",
        "gradient_start",
        "gradient_end",
        "text_color",
        "button_color",
        "button_text_color",
    )
    FONT_MAP = {
        "system-ui": (
            'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", '
            'Roboto, "Helvetica Neue", Arial, sans-serif'
        ),
        "Inter": '"Inter", sans-serif',
        "Roboto": '"Roboto", sans-serif',
        "Open Sans": '"Open Sans", sans-serif',
        "Lato": '"Lato", sans-serif',
        "Poppins": '"Poppins", sans-serif',
        "Georgia": "Georgia, serif",
    }
    RESETTABLE_FIELDS = (
        "template",
        "split_alignment",
        "card_background_color",
        "glassmorphism",
        "glassmorphism_blur",
        "glassmorphism_opacity",
        "company_logo",
        "favicon",
        "tagline",
        "primary_color",
        "secondary_color",
        "background_type",
        "background_color",
        "gradient_start",
        "gradient_end",
        "gradient_direction",
        "background_image",
        "background_overlay_opacity",
        "font_family",
        "text_color",
        "input_border_radius",
        "button_border_radius",
        "button_color",
        "button_text_color",
        "show_manage_databases",
        "show_powered_by_odoo",
        "custom_footer_text",
        "login_welcome_title",
        "login_welcome_subtitle",
        "signup_welcome_title",
        "signup_welcome_subtitle",
        "reset_welcome_title",
        "reset_welcome_subtitle",
        "page_title",
        "page_title_signup",
        "page_title_reset",
        "social_button_style",
        "hide_social_labels",
        "dark_mode",
        "show_loading_animation",
        "loading_animation_type",
        "powered_by_text",
        "powered_by_url",
        "custom_css",
        "terms_url",
        "privacy_url",
        "terms_label",
        "privacy_label",
    )
    BINARY_FIELDS = ("company_logo", "favicon", "background_image")
    VERSIONED_FIELDS = RESETTABLE_FIELDS
    RESET_SECTIONS = {
        "brand": (
            "company_logo",
            "favicon",
            "tagline",
            "primary_color",
            "secondary_color",
            "font_family",
            "text_color",
        ),
        "layout": (
            "template",
            "split_alignment",
            "card_background_color",
            "glassmorphism",
            "glassmorphism_blur",
            "glassmorphism_opacity",
            "input_border_radius",
            "button_border_radius",
            "button_color",
            "button_text_color",
            "dark_mode",
        ),
        "background": (
            "background_type",
            "background_color",
            "gradient_start",
            "gradient_end",
            "gradient_direction",
            "background_image",
            "background_overlay_opacity",
        ),
        "content": (
            "custom_footer_text",
            "login_welcome_title",
            "login_welcome_subtitle",
            "signup_welcome_title",
            "signup_welcome_subtitle",
            "reset_welcome_title",
            "reset_welcome_subtitle",
            "page_title",
            "page_title_signup",
            "page_title_reset",
            "terms_url",
            "privacy_url",
            "terms_label",
            "privacy_label",
        ),
        "advanced": (
            "show_manage_databases",
            "show_powered_by_odoo",
            "social_button_style",
            "hide_social_labels",
            "show_loading_animation",
            "loading_animation_type",
            "powered_by_text",
            "powered_by_url",
            "custom_css",
        ),
    }

    template = fields.Selection(
        [
            ("centered", "Centered Card"),
            ("split", "Split Screen"),
            ("fullbleed", "Full Bleed Background"),
            ("minimal", "Minimal"),
            ("sidebar", "Sidebar"),
        ],
        string="Template",
        default="centered",
        required=True,
    )
    split_alignment = fields.Selection(
        [("left", "Image on Left"), ("right", "Image on Right")],
        string="Split Alignment",
        default="left",
        help="Side for the image in Split Screen template",
    )
    card_background_color = fields.Char(
        string="Card Background Color", default="#FFFFFF"
    )
    glassmorphism = fields.Boolean(
        string="Enable Glassmorphism",
        default=False,
        help="Make the login card semi-transparent and blurred",
    )
    glassmorphism_blur = fields.Integer(string="Blur Factor (px)", default=10)
    glassmorphism_opacity = fields.Float(
        string="Card Opacity (0.0 - 1.0)", default=0.2
    )

    company_logo = fields.Binary(string="Company Logo")
    favicon = fields.Binary(string="Favicon")
    tagline = fields.Char(
        string="Tagline",
        help='Optional text shown below logo, e.g. "Welcome back."',
    )

    primary_color = fields.Char(
        string="Primary Color", default="#714B67", required=True
    )
    secondary_color = fields.Char(
        string="Secondary Color", default="#FFFFFF", required=True
    )
    background_type = fields.Selection(
        [
            ("solid", "Solid Color"),
            ("gradient", "Gradient"),
            ("animated_gradient", "Animated Gradient"),
            ("image", "Image"),
        ],
        string="Background Type",
        default="solid",
        required=True,
    )
    background_color = fields.Char(string="Background Color", default="#F8F9FA")
    gradient_start = fields.Char(string="Gradient Start", default="#714B67")
    gradient_end = fields.Char(string="Gradient End", default="#2B124C")
    gradient_direction = fields.Selection(
        [
            ("to right", "to right"),
            ("to bottom", "to bottom"),
            ("to bottom right", "to bottom right"),
            ("to bottom left", "to bottom left"),
        ],
        string="Gradient Direction",
        default="to bottom right",
    )
    background_image = fields.Binary(string="Background Image")
    background_overlay_opacity = fields.Float(
        string="Overlay Opacity",
        default=0.3,
        help="0.0 to 1.0, darkens image for text readability",
    )

    font_family = fields.Selection(
        [
            ("Inter", "Inter"),
            ("Roboto", "Roboto"),
            ("Open Sans", "Open Sans"),
            ("Lato", "Lato"),
            ("Poppins", "Poppins"),
            ("Georgia", "Georgia"),
            ("system-ui", "System Default"),
        ],
        string="Font Family",
        default="Inter",
        required=True,
    )
    text_color = fields.Char(string="Text Color", default="#212529", required=True)
    input_border_radius = fields.Integer(
        string="Input Border Radius (px)", default=6
    )
    button_border_radius = fields.Integer(
        string="Button Border Radius (px)", default=6
    )
    button_color = fields.Char(
        string="Button Color", default="#714B67", required=True
    )
    button_text_color = fields.Char(
        string="Button Text Color", default="#FFFFFF", required=True
    )

    show_manage_databases = fields.Boolean(
        string="Show Manage Databases", default=True
    )
    show_powered_by_odoo = fields.Boolean(
        string="Show Powered by Odoo", default=True
    )
    custom_footer_text = fields.Char(
        string="Custom Footer Text",
        help="Custom text shown in the footer, e.g. your helpdesk number",
    )
    login_welcome_title = fields.Char(
        string="Login Welcome Title",
        help='Override the default login heading, e.g. "Welcome back!"',
    )
    login_welcome_subtitle = fields.Char(
        string="Login Welcome Subtitle",
        help='A short subtitle below the title, e.g. "Sign in to continue."',
    )
    signup_welcome_title = fields.Char(
        string="Signup Welcome Title", default="Create your account"
    )
    signup_welcome_subtitle = fields.Char(
        string="Signup Welcome Subtitle", default="Join us in a few simple steps."
    )
    reset_welcome_title = fields.Char(
        string="Password Reset Title", default="Reset your password"
    )
    reset_welcome_subtitle = fields.Char(
        string="Password Reset Subtitle",
        default="We will help you get back into your account.",
    )
    page_title = fields.Char(
        string="Login Page Title", default="Sign in to {company}"
    )
    page_title_signup = fields.Char(
        string="Signup Page Title", default="Create an account | {company}"
    )
    page_title_reset = fields.Char(
        string="Password Reset Page Title", default="Reset password | {company}"
    )
    social_button_style = fields.Selection(
        [
            ("rounded", "Rounded"),
            ("pill", "Pill"),
            ("square", "Square"),
            ("icon", "Icon Focused"),
        ],
        string="Social Login Style",
        default="rounded",
        required=True,
    )
    hide_social_labels = fields.Boolean(string="Hide Social Login Labels")
    dark_mode = fields.Selection(
        [
            ("off", "Always Light"),
            ("auto", "Follow Device"),
            ("on", "Always Dark"),
        ],
        string="Dark Mode",
        default="off",
        required=True,
    )
    show_loading_animation = fields.Boolean(
        string="Show Loading Animation", default=True
    )
    loading_animation_type = fields.Selection(
        [
            ("spinner", "Spinner"),
            ("progress", "Progress Bar"),
            ("pulse", "Logo Pulse"),
        ],
        string="Loading Style",
        default="spinner",
        required=True,
    )
    powered_by_text = fields.Char(string="Powered-by Text", default="Powered by Odoo")
    powered_by_url = fields.Char(
        string="Powered-by URL", default="https://www.odoo.com"
    )
    custom_css = fields.Text(
        string="Custom CSS",
        help=(
            "Optional CSS overrides for advanced users. External resources, imports, "
            "scripts, and legacy executable CSS are blocked."
        ),
    )
    terms_url = fields.Char(string="Terms of Service URL")
    privacy_url = fields.Char(string="Privacy Policy URL")
    terms_label = fields.Char(string="Terms Label", default="Terms of Service")
    privacy_label = fields.Char(string="Privacy Label", default="Privacy Policy")

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
        index=True,
        ondelete="cascade",
    )
    active_version_id = fields.Many2one(
        "auth.branding.version",
        string="Published Version",
        copy=False,
        readonly=True,
        ondelete="set null",
    )
    version_ids = fields.One2many(
        "auth.branding.version", "config_id", string="Published Versions", readonly=True
    )
    published_at = fields.Datetime(
        related="active_version_id.published_at", string="Last Published", readonly=True
    )
    has_unpublished_changes = fields.Boolean(
        compute="_compute_has_unpublished_changes", string="Unpublished Changes"
    )

    @api.depends(*VERSIONED_FIELDS, "active_version_id", "active_version_id.settings_snapshot")
    def _compute_has_unpublished_changes(self):
        for config in self:
            if not config.active_version_id:
                config.has_unpublished_changes = True
                continue
            version_values = config._get_version_values(config.active_version_id)
            config.has_unpublished_changes = any(
                config[field_name] != version_values[field_name]
                for field_name in self.VERSIONED_FIELDS
            )

    @api.constrains(*COLOR_FIELDS)
    def _check_color_format(self):
        for record in self:
            invalid_fields = [
                record._fields[field_name].string
                for field_name in self.COLOR_FIELDS
                if (value := record[field_name])
                and not self.COLOR_PATTERN.fullmatch(value)
            ]
            if invalid_fields:
                raise ValidationError(
                    _(
                        "Colors must use the #RRGGBB format. Check: %(fields)s",
                        fields=", ".join(invalid_fields),
                    )
                )

    @api.constrains("terms_url", "privacy_url", "powered_by_url")
    def _check_url_format(self):
        for record in self:
            for field_name in ("terms_url", "privacy_url", "powered_by_url"):
                value = record[field_name]
                if not value:
                    continue
                if not self._is_safe_http_url(value):
                    raise ValidationError(
                        _(
                            "%(field)s must be a valid HTTP or HTTPS URL.",
                            field=record._fields[field_name].string,
                        )
                    )

    @staticmethod
    def _is_safe_http_url(value):
        try:
            parsed = urlsplit(value)
        except (TypeError, ValueError):
            return False
        return bool(
            value == value.strip()
            and parsed.scheme.lower() in {"http", "https"}
            and parsed.netloc
        )

    def _get_safe_external_url(self, field_name):
        self.ensure_one()
        if field_name not in {"terms_url", "privacy_url", "powered_by_url"}:
            return False
        value = self[field_name]
        return value if value and self._is_safe_http_url(value) else False

    @classmethod
    def _sanitize_custom_css(cls, value):
        if not value:
            return ""
        value = str(value)
        css_without_comments = re.sub(r"/\*.*?\*/", "", value, flags=re.DOTALL)
        if (
            len(value) > cls.CUSTOM_CSS_MAX_LENGTH
            or value.count("/*") != value.count("*/")
            or cls.UNSAFE_CSS_PATTERN.search(css_without_comments)
            or any(ord(character) < 32 and character not in "\n\r\t" for character in value)
        ):
            return ""
        return value

    @api.constrains("custom_css")
    def _check_custom_css(self):
        for record in self:
            if record.custom_css and not self._sanitize_custom_css(record.custom_css):
                raise ValidationError(
                    _(
                        "Custom CSS contains an unsafe or unsupported construct. "
                        "Remove HTML tags, external URLs, imports, scripts, or executable CSS."
                    )
                )

    def _get_snapshot_values(self):
        self.ensure_one()
        return {
            field_name: self[field_name]
            for field_name in self.VERSIONED_FIELDS
            if field_name not in self.BINARY_FIELDS
        }

    def _get_version_values(self, version):
        self.ensure_one()
        snapshot_fields = [
            field_name
            for field_name in self.VERSIONED_FIELDS
            if field_name not in self.BINARY_FIELDS
        ]
        defaults = self.default_get(snapshot_fields)
        values = {
            field_name: version.settings_snapshot.get(
                field_name, defaults.get(field_name, False)
            )
            for field_name in snapshot_fields
        }
        values.update(
            {field_name: version[field_name] for field_name in self.BINARY_FIELDS}
        )
        return values

    def _get_published_resource(self):
        self.ensure_one()
        return self.active_version_id or self

    def _get_frontend_values(self):
        self.ensure_one()
        if self.active_version_id:
            values = self._get_version_values(self.active_version_id)
        else:
            values = {field_name: self[field_name] for field_name in self.VERSIONED_FIELDS}
        values.update(
            {
                "company_id": self.company_id.id,
                "company_logo": bool(values.get("company_logo")),
                "favicon": bool(values.get("favicon")),
                "background_image": bool(values.get("background_image")),
                "terms_url": values.get("terms_url")
                if self._is_safe_http_url(values.get("terms_url") or "")
                else False,
                "privacy_url": values.get("privacy_url")
                if self._is_safe_http_url(values.get("privacy_url") or "")
                else False,
                "powered_by_url": values.get("powered_by_url")
                if self._is_safe_http_url(values.get("powered_by_url") or "")
                else False,
                "custom_css": self._sanitize_custom_css(values.get("custom_css")),
                "is_preview": False,
            }
        )
        return values

    @api.constrains("background_overlay_opacity", "glassmorphism_opacity")
    def _check_opacity_range(self):
        for record in self:
            for field_name in (
                "background_overlay_opacity",
                "glassmorphism_opacity",
            ):
                if not 0.0 <= record[field_name] <= 1.0:
                    raise ValidationError(
                        _(
                            "%(field)s must be between 0.0 and 1.0.",
                            field=record._fields[field_name].string,
                        )
                    )

    @api.constrains(
        "glassmorphism_blur",
        "input_border_radius",
        "button_border_radius",
    )
    def _check_non_negative_dimensions(self):
        for record in self:
            for field_name in (
                "glassmorphism_blur",
                "input_border_radius",
                "button_border_radius",
            ):
                if record[field_name] < 0:
                    raise ValidationError(
                        _(
                            "%(field)s must be positive or zero.",
                            field=record._fields[field_name].string,
                        )
                    )

    @api.constrains("company_id")
    def _check_company_unique(self):
        for record in self:
            if self.search_count(
                [
                    ("company_id", "=", record.company_id.id),
                    ("id", "!=", record.id),
                ]
            ):
                raise ValidationError(
                    _("The branding configuration must be unique per company.")
                )

    @api.model
    def _get_or_create_config(self, company_id=False):
        company = self.env["res.company"].browse(company_id).exists()
        company = company[:1] or self.env.company
        config = self.search([("company_id", "=", company.id)], limit=1)
        if not config:
            config = self.create({"company_id": company.id})
        elif not config.active_version_id:
            config.active_version_id = config._create_published_version()
        return config

    @api.model_create_multi
    def create(self, values_list):
        configs = super().create(values_list)
        for config in configs:
            config.active_version_id = config._create_published_version()
        return configs

    @api.model
    def _get_request_config(self, company_id=False):
        """Return branding only for a company available to the request user."""
        try:
            company_id = int(company_id)
        except (TypeError, ValueError):
            company_id = self.env.company.id
        if company_id not in self.env.user.company_ids.ids:
            company_id = self.env.company.id
        return (
            self.sudo()
            .with_company(company_id)
            ._get_or_create_config(company_id=company_id)
        )

    @api.model
    def get_or_create(self, company_id=False):
        """Compatibility alias; new code should use ``_get_or_create_config``."""
        warnings.warn(
            "auth.branding.config.get_or_create() is deprecated; "
            "use _get_or_create_config() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._get_or_create_config(company_id=company_id)

    def copy_data(self, default=None):
        raise UserError(
            _(
                "Branding configurations cannot be duplicated. "
                "Create or open the configuration for the target company instead."
            )
        )

    def action_reset_defaults(self):
        self.ensure_one()
        defaults = self.default_get(list(self.RESETTABLE_FIELDS))
        self.write(
            {
                field_name: defaults.get(field_name, False)
                for field_name in self.RESETTABLE_FIELDS
            }
        )
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_reset_section(self):
        self.ensure_one()
        section = self.env.context.get("auth_branding_reset_section")
        field_names = self.RESET_SECTIONS.get(section)
        if not field_names:
            raise UserError(_("Select a valid branding section to reset."))
        defaults = self.default_get(list(field_names))
        self.write(
            {
                field_name: defaults.get(field_name, False)
                for field_name in field_names
            }
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Section reset"),
                "message": _(
                    "The %(section)s settings were restored to their defaults.",
                    section=section.title(),
                ),
                "type": "success",
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

    def action_open_setup_wizard(self):
        self.ensure_one()
        wizard_fields = self.env["auth.branding.wizard"]._fields
        defaults = {
            f"default_{field_name}": self[field_name]
            for field_name in self.env["auth.branding.preset"].CONFIG_FIELDS
            if field_name in wizard_fields
        }
        defaults.update(
            {
                "default_config_id": self.id,
                "default_company_logo": self.company_logo,
                "default_tagline": self.tagline,
            }
        )
        action = self.env["ir.actions.actions"]._for_xml_id(
            "auth_branding.action_auth_branding_wizard"
        )
        action["context"] = {**self.env.context, **defaults}
        return action

    def _get_export_payload(self):
        self.ensure_one()

        def export_binary(value):
            if not value:
                return False
            if isinstance(value, bytes):
                return value.decode("ascii")
            return str(value)

        return {
            "format": self.EXPORT_FORMAT,
            "schema_version": self.EXPORT_SCHEMA_VERSION,
            "exported_at": fields.Datetime.to_string(fields.Datetime.now()),
            "company": self.company_id.display_name,
            "settings": self._get_snapshot_values(),
            "assets": {
                field_name: export_binary(self[field_name])
                for field_name in self.BINARY_FIELDS
            },
        }

    def action_export_branding(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/auth_branding/export/{self.id}",
            "target": "self",
        }

    def action_open_import_wizard(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "auth_branding.action_auth_branding_import_wizard"
        )
        action["context"] = {
            **self.env.context,
            "default_config_id": self.id,
        }
        return action

    def action_open_save_preset_wizard(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "auth_branding.action_auth_branding_preset_wizard"
        )
        action["context"] = {
            **self.env.context,
            "default_config_id": self.id,
        }
        return action

    def _create_published_version(self):
        self.ensure_one()
        published_at = fields.Datetime.now()
        return self.env["auth.branding.version"].sudo().create(
            {
                "name": _(
                    "%(company)s — %(date)s",
                    company=self.company_id.display_name,
                    date=fields.Datetime.to_string(published_at),
                ),
                "config_id": self.id,
                "settings_snapshot": self._get_snapshot_values(),
                "company_logo": self.company_logo,
                "favicon": self.favicon,
                "background_image": self.background_image,
                "published_at": published_at,
                "published_by": self.env.user.id,
            }
        )

    def action_publish(self):
        self.ensure_one()
        self.active_version_id = self._create_published_version()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Branding published"),
                "message": _("The new authentication experience is now live."),
                "type": "success",
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

    def _restore_version(self, version):
        self.ensure_one()
        if version.config_id != self:
            raise UserError(_("This version belongs to another configuration."))
        self.write(self._get_version_values(version))

    def action_discard_draft(self):
        self.ensure_one()
        if self.active_version_id:
            self._restore_version(self.active_version_id)
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_open_version_history(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "auth_branding.action_auth_branding_version"
        )
        action["domain"] = [("config_id", "=", self.id)]
        action["context"] = {"default_config_id": self.id, "create": False}
        return action

    def action_save(self):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Draft saved"),
                "message": _("Your changes are saved but are not published yet."),
                "type": "info",
            },
        }
