from urllib.parse import quote

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestAuthBrandingController(HttpCase):
    def test_theme_css_headers_and_conditional_request(self):
        response = self.url_open("/auth_branding/theme.css")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["Content-Type"].startswith("text/css"))
        self.assertEqual(
            response.headers["Cache-Control"],
            "public, max-age=3600, must-revalidate",
        )
        self.assertTrue(response.headers["ETag"])

        cached_response = self.url_open(
            "/auth_branding/theme.css",
            headers={"If-None-Match": response.headers["ETag"]},
        )
        self.assertEqual(cached_response.status_code, 304)

    def test_invalid_image_field_returns_not_found(self):
        response = self.url_open("/auth_branding/image/not_allowed")
        self.assertEqual(response.status_code, 404)

    def test_public_route_cannot_select_an_unrelated_company(self):
        other_company = self.env["res.company"].create(
            {"name": "Unrelated Branding Company"}
        )
        self.env["auth.branding.config"].sudo().create(
            {
                "company_id": other_company.id,
                "primary_color": "#010203",
            }
        )
        current_config = (
            self.env["auth.branding.config"]
            .sudo()
            ._get_or_create_config(self.env.company.id)
        )
        current_config.primary_color = "#445566"

        response = self.url_open(
            f"/auth_branding/theme.css?company_id={other_company.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("#445566", response.text)
        self.assertNotIn("#010203", response.text)

    def test_preview_css_parameters_are_sanitized(self):
        self.authenticate("admin", "admin")
        payload = "#fff;}</style><script>alert(1)</script>"
        response = self.url_open(
            "/auth_branding/preview?primary_color=" + quote(payload)
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("<script>alert(1)</script>", response.text)
