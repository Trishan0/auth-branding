from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAuthBrandingVersion(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({"name": "Versioned Brand"})
        cls.env.user.write({"company_ids": [(4, cls.company.id)]})
        cls.env = cls.env(context={
            **cls.env.context,
            "allowed_company_ids": [cls.env.company.id, cls.company.id],
        })
        cls.config = cls.env["auth.branding.config"].create(
            {"company_id": cls.company.id, "primary_color": "#112233"}
        )

    def test_draft_does_not_change_published_values(self):
        published_version = self.config.active_version_id
        self.assertFalse(self.config.has_unpublished_changes)

        self.config.primary_color = "#445566"
        self.assertTrue(self.config.has_unpublished_changes)
        self.assertEqual(
            self.config._get_frontend_values()["primary_color"], "#112233"
        )
        self.assertEqual(self.config._get_published_resource(), published_version)

    def test_discard_draft_restores_active_version(self):
        self.config.write({"primary_color": "#445566", "tagline": "Draft"})
        self.config.action_discard_draft()
        self.assertEqual(self.config.primary_color, "#112233")
        self.assertFalse(self.config.tagline)
        self.assertFalse(self.config.has_unpublished_changes)

    def test_restore_creates_a_new_audit_version(self):
        original = self.config.active_version_id
        self.config.primary_color = "#445566"
        self.config.action_publish()
        self.assertEqual(len(self.config.version_ids), 2)

        original.action_restore()
        self.assertEqual(len(self.config.version_ids), 3)
        self.assertEqual(self.config.primary_color, "#112233")
        self.assertEqual(
            self.config._get_frontend_values()["primary_color"], "#112233"
        )

    def test_published_version_must_match_configuration_company(self):
        other_company = self.env["res.company"].create({"name": "Other Brand"})
        self.env.user.write({"company_ids": [(4, other_company.id)]})
        other_config = self.env["auth.branding.config"].with_context(
            allowed_company_ids=[
                self.env.company.id,
                self.company.id,
                other_company.id,
            ]
        ).create({"company_id": other_company.id})

        with self.assertRaises(UserError), self.env.cr.savepoint():
            self.config.active_version_id = other_config.active_version_id
