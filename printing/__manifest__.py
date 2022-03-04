# -*- coding: utf-8 -*-
{
    'name': 'PRINTING',
    'version': '1.1',
    'summary': 'printing',
    'category': 'difmiadi',
    'description': u"""
This module configures your printing.
""",
    'author': 'Difference informatique - MIADI',
    'depends': [
        'base', 'base_setup'
        
    ],
    'data': [
        "wizard/wiz_print_etiquette.xml",
        "views/etiq_model_views.xml",
        "views/printer_views.xml",
        "views/parameter_views.xml",
        "printing_menu.xml",
       
        "security/ir.model.access.csv",
        
    ],
    'demo': [
        'data/printing_data.xml'
             ],
    'application': False,
    #'license': 'OPL-1',
   
  
}
