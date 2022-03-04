# -*- coding: utf-8 -*-
{
    'name': "hubi_sale_order_toinvoice",

    'summary': """
        hubi_sale_order_toinvoice""",

    
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
          'delivery',
          'stock',
          'hubi_menu',
          'sale_order_toinvoice_period',
                                        
        ],

    # always loaded
    'data': [
        "menu/hubi_menu.xml",         
     ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}