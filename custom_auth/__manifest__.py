{
    'name': 'Custom Auth',
    'version': '1.0',
    'summary': 'Custom Authentication Module with OTP',
    'description': """
        Custom Auth module with OTP verification during signup.
    """,
    'author': 'Sharan Gyawali'
              'Damodar Aryal',
    'category': 'Website',
    'depends': ['auth_signup','web','website','mental_health'],
    'data': [
        'data/email_template.xml',
        'views/otp_verification.xml',
        'views/signup_inherit.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
