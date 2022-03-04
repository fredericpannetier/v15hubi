# -*- coding: utf-8 -*-
{
    'name': "tools",

    'summary': """
        tools""",

    'description': """
      tools box
    """,

    'author': "Difference informatique-MIADI",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'difmiadi',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [  
                                                                       
        ],

    # always loaded
    'data': [  
        "security/ir.model.access.csv"                                                                            
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}