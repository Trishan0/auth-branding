{
    'name': 'Auth Branding',
    'version': '19.0.1.0.0',
    'author':'Trishan Fernando',
    'website':'trishanfernando.com',
    'category': 'Technical',
    'summary': 'Customize login, signup and password reset pages with live preview',
    'images': ['static/src/description/main_screenshot.png'],
    'description': """
        Auth Branding for Odoo 19
        =========================
        This module allows you to fully customize the appearance of Odoo's authentication pages (Login, Sign Up, Reset Password).
        
        Key Features:
        - Multiple Layouts: Centered, Split Screen, Full Bleed.
        - Backgrounds: Solid, Gradients, Animated Gradients, Images.
        - Modern Design: Glassmorphism effects (blur & opacity).
        - Branding: Custom logo, favicon, tagline, and footer text.
        - Styling: Control colors, fonts, and border radius.
        - Live Preview: See changes in real-time within the backend.
    """,
    'depends': ['web', 'auth_signup', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/auth_branding_settings_views.xml',
        'views/res_config_settings_views.xml',
        'views/auth_branding_templates.xml',
    ],
    "images": ['static/description/banner.gif','static/description/icon.jpg'],

    'assets': {
        'web.assets_backend': [
            'auth_branding/static/src/js/auth_branding_preview.js',
            'auth_branding/static/src/xml/auth_branding_preview.xml',
            'auth_branding/static/src/css/auth_branding_settings.css',
        ],
        'web.assets_frontend': [
            'auth_branding/static/src/css/auth_branding_frontend.css',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
