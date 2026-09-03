from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AuthBrandingVersion(models.Model):
    _name = "auth.branding.version"
    _description = "Authentication Branding Published Version"
    _order = "published_at desc, id desc"
    _check_company_auto = True

    name = fields.Char(required=True, readonly=True)
    config_id = fields.Many2one(
        "auth.branding.config",
        required=True,
        ondelete="cascade",
        index=True,
        check_company=True,
    )
    company_id = fields.Many2one(
        related="config_id.company_id", store=True, index=True
    )
    settings_snapshot = fields.Json(required=True, default=dict, readonly=True)
    company_logo = fields.Binary(readonly=True)
    favicon = fields.Binary(readonly=True)
    background_image = fields.Binary(readonly=True)
    published_at = fields.Datetime(required=True, default=fields.Datetime.now, readonly=True)
    published_by = fields.Many2one(
        "res.users", required=True, default=lambda self: self.env.user, readonly=True
    )
    is_active = fields.Boolean(compute="_compute_is_active")

    @api.depends("config_id.active_version_id")
    def _compute_is_active(self):
        for version in self:
            version.is_active = version.config_id.active_version_id == version

    def action_restore(self):
        self.ensure_one()
        self.config_id._restore_version(self)
        return self.config_id.action_publish()

    def unlink(self):
        if self.filtered("is_active"):
            raise UserError(_("The active branding version cannot be deleted."))
        return super().unlink()
