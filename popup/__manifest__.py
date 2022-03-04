# -*- coding: utf-8 -*-
{
    'name': "popup",

    'summary': """
        popup""",

    'description': """
      Developper tool to show a popup message
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': '',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [   
        'base',
        'base_setup',                                                    
        ],

    # always loaded
    'data': [  
        'security/ir.model.access.csv',          
        'views/di_wiz_popup.xml',                                                                            
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
    'license': 'OPL-1',
}