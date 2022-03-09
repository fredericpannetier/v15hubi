# See LICENSE file for full copyright and licensing details.

{
    'name': 'Accounting Transfer',
    'version': '14.0.1.0.0',
    'category': 'Accounting/Accounting',
    'author': 'Difference informatique - MIADI',
    
    'summary': 'Accounting Transfer',
    'depends': [
        'base','base_setup','sale', 'account_payment_partner', 'account_payment_mode', 'tools'
    ],
    'data': ['data/template_email.xml',
             'data/account_default_settings.xml',
        'views/inh_parameter_config_views.xml',
        'views/inh_partner_views.xml',
        'views/inh_account_move_views.xml',
        'views/inh_account_payment_mode.xml',
        #'wizard/wiz_accounting_parameter_views.xml',
        'wizard/wiz_transfert_compta_views.xml',
        'accounting_transfer_menu.xml',
        
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
