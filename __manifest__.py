# -*- coding: utf-8 -*-
{
    'name': "odooThrones",

    'summary': "El mejor juego de odoo.",

    'description': """
Long description of module's purpose
    """,

    'author': "muvbit",
    'website': "https://www.muvment.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/wizards_views.xml',
        'views/templates.xml',
        'data/cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
