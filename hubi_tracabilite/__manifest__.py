# -*- coding: utf-8 -*-
{
    'name': "hubi_tracabilite",

    'summary': """
        hubi_tracabilite""",

    
    'author': "Difference informatique - MIADI",
   
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HUBI',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [  
          'base',
          'product',
          'stock',
          'hubi_menu',
                                        
        ],

    # always loaded
    'data': [
              'views/inh_location_views.xml',
              'views/tracabilite_views.xml',
              'wizards/wiz_tracabilite_views.xml',
              'security/ir.model.access.csv',   
              'menu/hubi_menu.xml'
     ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}