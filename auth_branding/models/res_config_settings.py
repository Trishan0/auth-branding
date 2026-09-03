from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auth_branding_config_id = fields.Many2one(
        "auth.branding.config",
        string="Authentication Branding Configuration",
        compute="_compute_auth_branding_config_id",
        compute_sudo=True,
    )

    @api.depends("company_id")
    def _compute_auth_branding_config_id(self):
        Config = self.env["auth.branding.config"]
        for settings in self:
            company = settings.company_id or self.env.company
            settings.auth_branding_config_id = Config.search(
                [("company_id", "=", company.id)], limit=1
            )
