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

        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.config.write({"powered_by_url": "javascript:alert(1)"})

    def test_presentation_defaults(self):
        self.assertEqual(self.config.dark_mode, "off")
        self.assertTrue(self.config.show_loading_animation)
        self.assertEqual(self.config.loading_animation_type, "spinner")
        self.assertEqual(self.config.powered_by_text, "Powered by Odoo")

    def test_custom_css_blocks_active_content_and_external_resources(self):
        for unsafe_css in (
            'body { background: url("https://tracker.example/pixel"); }',
            "</style><script>alert(1)</script>",
            "@import 'https://example.com/theme.css';",
            "div { width: expression(alert(1)); }",
            "body { background: u/**/rl(https://tracker.example); }",
            "body { background: u\\72l(https://tracker.example); }",
            'body { background: image-set("//tracker.example/pixel"); }',
        ):
            with self.subTest(css=unsafe_css), self.assertRaises(
                ValidationError
            ), self.env.cr.savepoint():
                self.config.custom_css = unsafe_css

    def test_custom_css_accepts_local_style_overrides(self):
        css = ".oe_login_form { max-width: 30rem; }"
        self.config.custom_css = css
        self.assertEqual(self.config.custom_css, css)

    def test_export_payload_is_portable_and_excludes_technical_fields(self):
        payload = self.config._get_export_payload()
        self.assertEqual(payload["format"], "odoo_auth_branding")
        self.assertEqual(payload["schema_version"], 1)
        self.assertIn("primary_color", payload["settings"])
        self.assertIn("company_logo", payload["assets"])
        self.assertNotIn("company_id", payload["settings"])
        self.assertNotIn("active_version_id", payload["settings"])

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

    def test_reset_section_preserves_other_sections(self):
        self.config.write(
            {
                "primary_color": "#123456",
                "tagline": "Custom brand",
                "template": "fullbleed",
                "custom_footer_text": "Keep this content",
            }
        )
        action = self.config.with_context(
            auth_branding_reset_section="brand"
        ).action_reset_section()

        self.assertEqual(self.config.primary_color, "#714B67")
        self.assertFalse(self.config.tagline)
        self.assertEqual(self.config.template, "fullbleed")
        self.assertEqual(self.config.custom_footer_text, "Keep this content")
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["next"]["tag"], "reload")

    def test_reset_section_rejects_unknown_context(self):
        with self.assertRaises(UserError):
            self.config.with_context(
                auth_branding_reset_section="unknown"
            ).action_reset_section()

    def test_duplicate_action_is_blocked(self):
        with self.assertRaises(UserError):
            self.config.copy_data()
