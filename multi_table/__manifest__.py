# -*- coding: utf-8 -*-
{
    'name': "multi_table",

    'summary': """
        multi_table""",

    'description': """
      Table with multiple uses
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'difmiadi',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [   
        'base',                                                        
        ],

    # always loaded
    'data': [  
        'security/ir.model.access.csv',
        "views/di_multi_table_view.xml",                                                                      
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}