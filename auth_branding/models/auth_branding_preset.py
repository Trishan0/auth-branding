from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .auth_branding_config import AuthBrandingConfig


class AuthBrandingPreset(models.Model):
    _name = "auth.branding.preset"
    _description = "Authentication Branding Preset"
    _order = "sequence, name, id"

    CONFIG_FIELDS = (
        "template",
        "split_alignment",
        "card_background_color",
        "glassmorphism",
        "glassmorphism_blur",
        "glassmorphism_opacity",
        "primary_color",
        "secondary_color",
        "background_type",
        "background_color",
        "gradient_start",
        "gradient_end",
        "gradient_direction",
        "background_overlay_opacity",
        "font_family",
        "text_color",
        "input_border_radius",
        "button_border_radius",
        "button_color",
        "button_text_color",
    )

    name = fields.Char(required=True, translate=True)
    description = fields.Char(translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    is_system = fields.Boolean(default=False, readonly=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        index=True,
        ondelete="cascade",
        help="Leave empty to make this preset available to every company.",
    )

    template = fields.Selection(
        [
            ("centered", "Centered Card"),
            ("split", "Split Screen"),
            ("fullbleed", "Full Bleed Background"),
        ],
        default="centered",
        required=True,
    )
    split_alignment = fields.Selection(
        [("left", "Image on Left"), ("right", "Image on Right")],
        default="left",
    )
    card_background_color = fields.Char(default="#FFFFFF", required=True)
    glassmorphism = fields.Boolean(default=False)
    glassmorphism_blur = fields.Integer(default=10)
    glassmorphism_opacity = fields.Float(default=0.2)
    primary_color = fields.Char(default="#714B67", required=True)
    secondary_color = fields.Char(default="#FFFFFF", required=True)
    background_type = fields.Selection(
        [
            ("solid", "Solid Color"),
            ("gradient", "Gradient"),
            ("animated_gradient", "Animated Gradient"),
            ("image", "Image"),
        ],
        default="solid",
        required=True,
    )
    background_color = fields.Char(default="#F8F9FA", required=True)
    gradient_start = fields.Char(default="#714B67", required=True)
    gradient_end = fields.Char(default="#2B124C", required=True)
    gradient_direction = fields.Selection(
        [
            ("to right", "to right"),
            ("to bottom", "to bottom"),
            ("to bottom right", "to bottom right"),
            ("to bottom left", "to bottom left"),
        ],
        default="to bottom right",
        required=True,
    )
    background_overlay_opacity = fields.Float(default=0.3)
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
        default="Inter",
        required=True,
    )
    text_color = fields.Char(default="#212529", required=True)
    input_border_radius = fields.Integer(default=6)
    button_border_radius = fields.Integer(default=6)
    button_color = fields.Char(default="#714B67", required=True)
    button_text_color = fields.Char(default="#FFFFFF", required=True)

    @api.model
    def get_editor_fields(self):
        return ["id", "name", "description", "is_system", *self.CONFIG_FIELDS]

    @api.constrains(*AuthBrandingConfig.COLOR_FIELDS)
    def _check_color_format(self):
        for preset in self:
            if any(
                not AuthBrandingConfig.COLOR_PATTERN.fullmatch(preset[field_name])
                for field_name in AuthBrandingConfig.COLOR_FIELDS
            ):
                raise ValidationError(_("Preset colors must use the #RRGGBB format."))

    @api.constrains("background_overlay_opacity", "glassmorphism_opacity")
    def _check_opacity_range(self):
        for preset in self:
            if not 0.0 <= preset.background_overlay_opacity <= 1.0:
                raise ValidationError(_("Overlay opacity must be between 0.0 and 1.0."))
            if not 0.0 <= preset.glassmorphism_opacity <= 1.0:
                raise ValidationError(_("Card opacity must be between 0.0 and 1.0."))

    @api.constrains(
        "glassmorphism_blur", "input_border_radius", "button_border_radius"
    )
    def _check_non_negative_dimensions(self):
        for preset in self:
            if any(
                preset[field_name] < 0
                for field_name in (
                    "glassmorphism_blur",
                    "input_border_radius",
                    "button_border_radius",
                )
            ):
                raise ValidationError(_("Preset dimensions must be positive or zero."))

    def get_values_for_editor(self):
        self.ensure_one()
        return {field_name: self[field_name] for field_name in self.CONFIG_FIELDS}

    def apply_preset(self, config_id):
        self.ensure_one()
        config = self.env["auth.branding.config"].browse(config_id).exists()
        if not config:
            raise UserError(_("The branding configuration no longer exists."))
        config.write(self.get_values_for_editor())
        return True

    @api.model
    def create_from_config(self, config_id, name):
        config = self.env["auth.branding.config"].browse(config_id).exists()
        if not config:
            raise UserError(_("The branding configuration no longer exists."))
        values = {
            field_name: config[field_name] for field_name in self.CONFIG_FIELDS
        }
        values.update({"name": name, "company_id": config.company_id.id})
        return self.create(values).id

    @api.model_create_multi
    def create(self, values_list):
        if not self.env.su:
            for values in values_list:
                values["is_system"] = False
        return super().create(values_list)

    def write(self, values):
        if not self.env.su and self.filtered("is_system"):
            raise UserError(_("Built-in branding presets cannot be modified."))
        return super().write(values)

    def unlink(self):
        if not self.env.su and self.filtered("is_system"):
            raise UserError(_("Built-in branding presets cannot be deleted."))
        return super().unlink()
