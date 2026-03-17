{
    'name': 'Auth Branding',
    'version': '19.0.1.0.0',
    'author':'Trishan Fernando',
    'category': 'Technical',
    'summary': 'Customize login, signup and password reset pages with live preview',
    'depends': ['web', 'auth_signup', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/auth_branding_settings_views.xml',
        'views/res_config_settings_views.xml',
        'views/auth_branding_templates.xml',
    ],
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
