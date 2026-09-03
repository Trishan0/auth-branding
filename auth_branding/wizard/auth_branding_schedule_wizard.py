from datetime import timedelta

from odoo import _, fields, models


class AuthBrandingScheduleWizard(models.TransientModel):
    _name = "auth.branding.schedule.wizard"
    _description = "Schedule Authentication Branding Publish"

    config_id = fields.Many2one("auth.branding.config", required=True)
    company_id = fields.Many2one(
        "res.company", related="config_id.company_id", readonly=True
    )
    scheduled_at = fields.Datetime(
        string="Publish At",
        required=True,
        default=lambda self: fields.Datetime.now() + timedelta(hours=1),
    )
    note = fields.Char(string="Release Note")

    def action_schedule(self):
        self.ensure_one()
        self.env["auth.branding.schedule"].create_from_config(
            self.config_id, self.scheduled_at, self.note
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Branding scheduled"),
                "message": _(
                    "This draft snapshot will publish automatically at %(date)s.",
                    date=fields.Datetime.to_string(self.scheduled_at),
                ),
                "type": "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
