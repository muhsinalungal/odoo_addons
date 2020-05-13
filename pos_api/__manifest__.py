# -*- coding: utf-8 -*-
{
    'name': "pos_api",

    'summary': """
        Module containing pos api's""",

    'description': """
        Module containing pos api's
    """,

    'author': "Muhsin K",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'POS',
    'version': '13.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'as_time'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
