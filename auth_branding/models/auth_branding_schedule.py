from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AuthBrandingSchedule(models.Model):
    _name = "auth.branding.schedule"
    _description = "Authentication Branding Scheduled Publish"
    _order = "scheduled_at desc, id desc"
    _IMMUTABLE_FIELDS = {
        "name",
        "config_id",
        "scheduled_at",
        "note",
        "settings_snapshot",
        "company_logo",
        "favicon",
        "background_image",
        "created_by",
    }

    name = fields.Char(required=True, readonly=True)
    config_id = fields.Many2one(
        "auth.branding.config", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        related="config_id.company_id", store=True, index=True
    )
    scheduled_at = fields.Datetime(required=True, readonly=True, index=True)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("published", "Published"),
            ("cancelled", "Cancelled"),
            ("failed", "Failed"),
        ],
        required=True,
        default="pending",
        readonly=True,
        index=True,
    )
    note = fields.Char(readonly=True)
    settings_snapshot = fields.Json(required=True, default=dict, readonly=True)
    company_logo = fields.Binary(readonly=True)
    favicon = fields.Binary(readonly=True)
    background_image = fields.Binary(readonly=True)
    created_by = fields.Many2one(
        "res.users", required=True, default=lambda self: self.env.user, readonly=True
    )
    executed_at = fields.Datetime(readonly=True)
    version_id = fields.Many2one(
        "auth.branding.version", readonly=True, ondelete="set null"
    )
    error_message = fields.Text(readonly=True)

    @api.model_create_multi
    def create(self, values_list):
        now = fields.Datetime.now()
        for values in values_list:
            scheduled_at = fields.Datetime.to_datetime(values.get("scheduled_at"))
            if not scheduled_at or scheduled_at <= now:
                raise ValidationError(_("The publish time must be in the future."))
            config = self.env["auth.branding.config"].browse(
                values.get("config_id")
            ).exists()
            if not config:
                raise ValidationError(_("Select a valid branding configuration."))
            config.ensure_one()
            values["name"] = _(
                "%(company)s — %(date)s",
                company=config.company_id.display_name,
                date=fields.Datetime.to_string(scheduled_at),
            )
            values["state"] = "pending"
            values["created_by"] = self.env.user.id
            values.setdefault("settings_snapshot", config._get_snapshot_values())
            for field_name in config.BINARY_FIELDS:
                values.setdefault(field_name, config[field_name])
        return super().create(values_list)

    def write(self, values):
        if self._IMMUTABLE_FIELDS.intersection(values):
            raise UserError(_("A scheduled branding snapshot cannot be edited."))
        return super().write(values)

    @api.model
    def create_from_config(self, config, scheduled_at, note=False):
        config.ensure_one()
        return self.create(
            {
                "config_id": config.id,
                "scheduled_at": scheduled_at,
                "note": note,
            }
        )

    def action_cancel(self):
        self.ensure_one()
        if self.state != "pending":
            raise UserError(_("Only a pending publish can be cancelled."))
        self.state = "cancelled"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Scheduled publish cancelled"),
                "message": _("The captured branding snapshot will not be published."),
                "type": "info",
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

    def _execute_publish(self, executed_at):
        self.ensure_one()
        assets = {
            field_name: self[field_name]
            for field_name in self.config_id.BINARY_FIELDS
        }
        version = self.config_id._create_published_version(
            settings_snapshot=self.settings_snapshot,
            assets=assets,
            published_at=executed_at,
            published_by=self.created_by.id,
        )
        self.config_id.sudo().active_version_id = version
        self.sudo().write(
            {
                "state": "published",
                "executed_at": executed_at,
                "version_id": version.id,
                "error_message": False,
            }
        )

    @api.model
    def _run_due_schedules(self, now=None):
        executed_at = fields.Datetime.to_datetime(now) or fields.Datetime.now()
        schedules = self.sudo().search(
            [
                ("state", "=", "pending"),
                ("scheduled_at", "<=", executed_at),
            ],
            order="scheduled_at, id",
        )
        for schedule in schedules:
            try:
                with self.env.cr.savepoint():
                    schedule._execute_publish(executed_at)
            except Exception as error:  # cron must continue with the next company
                schedule.sudo().write(
                    {
                        "state": "failed",
                        "executed_at": executed_at,
                        "error_message": str(error)[:1000],
                    }
                )
        return len(schedules)
