from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestAuthBrandingConfig(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({"name": "Branding Test"})
        cls.env.user.write({"company_ids": [(4, cls.company.id)]})
        cls.env = cls.env(context={
            **cls.env.context,
            "allowed_company_ids": [cls.env.company.id, cls.company.id],
        })
        cls.config = cls.env["auth.branding.config"].create(
            {"company_id": cls.company.id}
        )

    def test_get_or_create_is_stable_per_company(self):
        first = self.env["auth.branding.config"]._get_or_create_config(
            self.company.id
        )
        second = self.env["auth.branding.config"]._get_or_create_config(
            self.company.id
        )
        self.assertEqual(first, self.config)
        self.assertEqual(second, self.config)

    def test_company_configuration_is_unique(self):
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.env["auth.branding.config"].create(
                {"company_id": self.company.id}
            )

    def test_color_validation_rejects_css_injection(self):
        with self.assertRaisesRegex(
            ValidationError, "#RRGGBB"
        ), self.env.cr.savepoint():
            self.config.write({"primary_color": "red;}</style><script>"})

    def test_color_validation_accepts_six_digit_hex(self):
        self.config.write({"primary_color": "#aBc123"})
        self.assertEqual(self.config.primary_color, "#aBc123")

    def test_url_validation(self):
        for invalid_url in (
            "javascript:alert(1)",
            "data:text/html,test",
            " https://example.com",
        ):
            with self.subTest(url=invalid_url), self.assertRaises(
                ValidationError
            ), self.env.cr.savepoint():
                self.config.write({"terms_url": invalid_url})
        self.config.write({"terms_url": "https://example.com/terms"})

    def test_opacity_and_dimension_validation(self):
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.config.write({"background_overlay_opacity": 1.1})
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.config.write({"glassmorphism_blur": -1})

    def test_reset_defaults(self):
        self.config.write(
            {
                "primary_color": "#123456",
                "tagline": "Custom",
                "show_powered_by_odoo": False,
            }
        )
        action = self.config.action_reset_defaults()
        self.assertEqual(self.config.primary_color, "#714B67")
        self.assertFalse(self.config.tagline)
        self.assertTrue(self.config.show_powered_by_odoo)
        self.assertEqual(action["tag"], "reload")

    def test_duplicate_action_is_blocked(self):
        with self.assertRaises(UserError):
            self.config.copy_data()
