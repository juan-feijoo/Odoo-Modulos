{
    'name': 'Custom Sign Restriction',
    'version': '1.0',
    'depends': ['web', 'sign'],
    'assets': {
        'web.assets_backend': [
            'custom_sign_restriction/static/src/js/name_and_signature_patch.js',
            'custom_sign_restriction/static/src/css/signature_styles.css',
        ],
        'web.assets_frontend': [
            'custom_sign_restriction/static/src/js/name_and_signature_patch.js',
            'custom_sign_restriction/static/src/css/signature_styles.css',
        ],
        'sign.assets_public_sign': [
            'custom_sign_restriction/static/src/js/name_and_signature_patch.js',
            'custom_sign_restriction/static/src/css/signature_styles.css',
        ],
    },
    'installable': True,
    'license': 'OEEL-1',
}