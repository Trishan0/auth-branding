from odoo import _, fields, models


class AuthBrandingPresetWizard(models.TransientModel):
    _name = "auth.branding.preset.wizard"
    _description = "Save Authentication Branding Preset"
    _check_company_auto = True

    config_id = fields.Many2one(
        "auth.branding.config", required=True, check_company=True
    )
    company_id = fields.Many2one(
        "res.company", related="config_id.company_id", readonly=True
    )
    name = fields.Char(string="Theme Name", required=True)
    description = fields.Char(string="Short Description")

    def action_save(self):
        self.ensure_one()
        self.env["auth.branding.preset"].create_from_config(
            self.config_id.id, self.name, self.description
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Theme saved"),
                "message": _("The current visual settings are now reusable."),
                "type": "success",
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }
