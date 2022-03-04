# -*- coding: utf-8 -*-
{
    'name': "edi_ftp",

    'summary': """
        edi_ftp""",

    'description': """
       Module EDI
    """,

    'author': "Difference informatique - MIADI",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'difmiadi',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [   
        'base','base_setup','product','sale'                 
        ],


    # always loaded
    'data': [  
        'views/inh_parameter_config_views.xml',      
        'views/inh_partner_views.xml',
        'wizard/wiz_dialog_views.xml',
        'wizard/wiz_transfer_edi_views.xml',
        'edi_menu.xml',
        'security/ir.model.access.csv'

    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}