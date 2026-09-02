from odoo import _, api, fields, models

from ..models.auth_branding_color_utils import extract_logo_palette


class AuthBrandingWizard(models.TransientModel):
    _name = "auth.branding.wizard"
    _description = "Authentication Branding Quick Setup"

    state = fields.Selection(
        [
            ("identity", "Brand Identity"),
            ("style", "Style & Preview"),
            ("review", "Review & Apply"),
        ],
        default="identity",
        required=True,
    )
    config_id = fields.Many2one("auth.branding.config", required=True)
    company_id = fields.Many2one(
        "res.company", related="config_id.company_id", readonly=True
    )
    company_logo = fields.Binary(string="Company Logo")
    tagline = fields.Char(string="Tagline")
    preset_id = fields.Many2one(
        "auth.branding.preset",
        string="Starting Theme",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    suggested_primary_color = fields.Char(readonly=True)
    suggested_secondary_color = fields.Char(readonly=True)

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
    primary_color = fields.Char(default="#714B67", required=True)
    secondary_color = fields.Char(default="#FFFFFF", required=True)
    background_type = fields.Selection(
        [
            ("solid", "Solid Color"),
            ("gradient", "Gradient"),
            ("animated_gradient", "Animated Gradient"),
            ("image", "Image"),
        ],
        default="gradient",
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
    card_background_color = fields.Char(default="#FFFFFF", required=True)
    glassmorphism = fields.Boolean(default=False)
    glassmorphism_blur = fields.Integer(default=10)
    glassmorphism_opacity = fields.Float(default=0.2)
    input_border_radius = fields.Integer(default=6)
    button_border_radius = fields.Integer(default=6)
    button_color = fields.Char(default="#714B67", required=True)
    button_text_color = fields.Char(default="#FFFFFF", required=True)

    @api.onchange("company_logo")
    def _onchange_company_logo(self):
        if not self.company_logo:
            self.suggested_primary_color = False
            self.suggested_secondary_color = False
            return
        palette = extract_logo_palette(self.company_logo)
        if palette:
            self.suggested_primary_color = palette[0]
            self.primary_color = palette[0]
            self.button_color = palette[0]
            self.gradient_start = palette[0]
        if len(palette) > 1:
            self.suggested_secondary_color = palette[1]
            self.gradient_end = palette[1]

    @api.onchange("preset_id")
    def _onchange_preset_id(self):
        if not self.preset_id:
            return
        for field_name, value in self.preset_id.get_values_for_editor().items():
            if field_name in self._fields:
                self[field_name] = value
        if self.suggested_primary_color:
            self.primary_color = self.suggested_primary_color
            self.button_color = self.suggested_primary_color
            self.gradient_start = self.suggested_primary_color
        if self.suggested_secondary_color:
            self.gradient_end = self.suggested_secondary_color

    def action_next(self):
        self.ensure_one()
        self.state = "style" if self.state == "identity" else "review"
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_previous(self):
        self.ensure_one()
        self.state = "identity" if self.state == "style" else "style"
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_apply(self):
        self.ensure_one()
        values = {
            field_name: self[field_name]
            for field_name in self.env["auth.branding.preset"].CONFIG_FIELDS
            if field_name in self._fields
        }
        values.update({"company_logo": self.company_logo, "tagline": self.tagline})
        self.config_id.write(values)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Branding applied"),
                "message": _("Your authentication branding has been updated."),
                "type": "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
