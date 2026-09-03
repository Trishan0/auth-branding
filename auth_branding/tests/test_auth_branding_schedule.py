from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestAuthBrandingSchedule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({"name": "Scheduled Branding"})
        cls.env.user.write({"company_ids": [(4, cls.company.id)]})
        cls.env = cls.env(
            context={
                **cls.env.context,
                "allowed_company_ids": [cls.env.company.id, cls.company.id],
            }
        )
        cls.config = cls.env["auth.branding.config"].create(
            {"company_id": cls.company.id}
        )

    def _schedule(self, **values):
        self.config.write(
            {
                "primary_color": values.get("primary_color", "#123456"),
                "tagline": values.get("tagline", "Scheduled snapshot"),
            }
        )
        scheduled_at = fields.Datetime.now() + timedelta(hours=1)
        return self.env["auth.branding.schedule"].create_from_config(
            self.config, scheduled_at, "Campaign launch"
        )

    def test_schedule_publishes_captured_snapshot_not_later_draft(self):
        schedule = self._schedule()
        self.config.write(
            {"primary_color": "#654321", "tagline": "Later draft"}
        )

        processed = self.env["auth.branding.schedule"]._run_due_schedules(
            now=schedule.scheduled_at + timedelta(minutes=1)
        )

        self.assertEqual(processed, 1)
        self.assertEqual(schedule.state, "published")
        self.assertEqual(schedule.version_id, self.config.active_version_id)
        published = self.config._get_frontend_values()
        self.assertEqual(published["primary_color"], "#123456")
        self.assertEqual(published["tagline"], "Scheduled snapshot")
        self.assertEqual(self.config.primary_color, "#654321")

    def test_cancelled_schedule_is_not_published(self):
        schedule = self._schedule(primary_color="#234567")
        active_version = self.config.active_version_id
        action = schedule.action_cancel()

        processed = self.env["auth.branding.schedule"]._run_due_schedules(
            now=schedule.scheduled_at + timedelta(minutes=1)
        )

        self.assertEqual(processed, 0)
        self.assertEqual(schedule.state, "cancelled")
        self.assertEqual(self.config.active_version_id, active_version)
        self.assertEqual(action["params"]["next"]["tag"], "reload")
        with self.assertRaises(UserError):
            schedule.action_cancel()

    def test_schedule_rejects_past_time(self):
        with self.assertRaises(ValidationError):
            self.env["auth.branding.schedule"].create_from_config(
                self.config,
                fields.Datetime.now() - timedelta(minutes=1),
            )

    def test_captured_snapshot_is_immutable(self):
        schedule = self._schedule()
        with self.assertRaises(UserError):
            schedule.write({"settings_snapshot": {"primary_color": "#FFFFFF"}})
