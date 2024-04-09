# -*- coding: utf-8 -*-
{
    'name': "mental_health",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        This module is made for the scheduling of the appointment of mental health related patient
    """,

    'author': "Damodar Aryal",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'application':True,
    'sequence':"1",

    # any module necessary for this one to work correctly
    'depends': ['base','website','mail'],

    # always loaded
    'data': [
        'security/security_groups.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/email_templates.xml',
        'data/timezone_data.xml',
        'data/ir_sequence.xml',
        'views/views.xml',
        'views/wizard_view.xml',
        'static/src/xml/nav_menu.xml',
        'static/src/xml/about_us.xml',
        'static/src/xml/book_appointment.xml',
        'static/src/xml/contact_us.xml',
        'static/src/xml/home.xml',
        'static/src/xml/practice_info.xml',
        'static/src/xml/services.xml',
        'views/templates.xml',
        'views/auth_inherit.xml',
        'views/show_patient_history.xml',
    ],
    'assets':{
        'web.assets_frontend':[
            '/mental_health/static/src/js/contact_us.js',
            '/mental_health/static/src/js/doctor_appointment_control.js',
            '/mental_health/static/src/js/delete_user.js',
            "/mental_health/static/src/css/reset.scss",
            "/mental_health/static/src/css/global.scss",
            "/mental_health/static/src/css/utils.scss",
            "/mental_health/static/src/css/style.scss",
        ]
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
