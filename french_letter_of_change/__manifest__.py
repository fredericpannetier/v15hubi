# Copyright 2014-2020 Akretion France (http://www.akretion.com/)
# @author: MIADI


{
    "name": "French Letter of Change",
    "summary": "Create French LCR CFONB files",
    "version": "14.0.1.0.0",
    "category": 'difmiadi',
    'author': 'Difference informatique - MIADI',

    "depends": [
        "account_payment_order", "tools"
        ],
        
    #"external_dependencies": {"python": ["unidecode"],},
    
    "data": [
        "data/account_payment_method.xml"
        ],
        
    "demo": [
        "demo/lcr_demo.xml"
        ],
    
    "post_init_hook": "update_bank_journals",
    "installable": True,
    'license': 'OPL-1',
}
