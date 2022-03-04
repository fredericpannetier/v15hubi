# -*- coding: utf-8 -*-
{
    'name': "hubi_palletization",

    'summary': """
        hubi_palletization""",

    
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
         
          'palletization',
                                        
        ],

    # always loaded
    'data': [
            "views/inh_palletization_views.xml",
            #"reports/inh_sale_order_report_views.xml",
            #"reports/inh_sale_carrier_report.xml",     
     ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}