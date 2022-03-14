# -*- coding: utf-8 -*-
{
    'name': "hubi_french_letter_of_change",

    'summary': """
        hubi_french_letter_of_change""",

    
    'author': "Difference informatique - MIADI",
   
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HUBI',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [  
          'base',
          'account_payment_mode',
          'account_payment_partner',
          'account_payment_order',
          'french_letter_of_change',
          'hubi_menu',                             
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
    'license': 'OPL-1',
}