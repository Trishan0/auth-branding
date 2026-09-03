{
    "name": "Auth Branding",
    "version": "19.0.2.0.0",
    "author": "Trishan Fernando",
    "maintainer": "Trishan Fernando",
    "maintainers": ["Trishan Fernando"],
    "website": "https://trishanfernando.com",
    "category": "Technical",
    "summary": "Visual auth page studio with presets, live preview and safe publishing",
    "description": """
Auth Branding for Odoo 19
=========================

Build company-specific authentication pages with guided themes, instant responsive
preview, accessible styling, draft publishing, rollback, and portable brand packages.
    """,
    "depends": ["web", "auth_signup", "base_setup"],
    "data": [
        "security/auth_branding_security.xml",
        "security/ir.model.access.csv",
        "data/auth_branding_preset_data.xml",
        "data/auth_branding_cron.xml",
        "wizard/auth_branding_wizard_views.xml",
        "wizard/auth_branding_schedule_wizard_views.xml",
        "views/auth_branding_version_views.xml",
        "views/auth_branding_schedule_views.xml",
        "views/auth_branding_settings_views.xml",
        "views/res_config_settings_views.xml",
        "views/auth_branding_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "auth_branding/static/src/js/auth_branding_preview.js",
            "auth_branding/static/src/js/auth_branding_preset_gallery.js",
            "auth_branding/static/src/js/auth_branding_accessibility.js",
            "auth_branding/static/src/xml/auth_branding_preview.xml",
            "auth_branding/static/src/xml/auth_branding_preset_gallery.xml",
            "auth_branding/static/src/xml/auth_branding_accessibility.xml",
            "auth_branding/static/src/css/auth_branding_settings.css",
        ],
        "web.assets_frontend": [
            "auth_branding/static/src/css/auth_branding_frontend.css",
            "auth_branding/static/src/js/auth_branding_frontend.js",
            "auth_branding/static/src/js/auth_branding_preview_receiver.js",
        ],
        "web.assets_unit_tests": [
            "auth_branding/static/tests/**/*.test.js",
        ],
    },
    "images": [
        "static/description/banner.png",
        "static/description/icon.png",
    ],
    "development_status": "Beta",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
