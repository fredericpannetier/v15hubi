# See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Update Miadi',
    'version': '14.0.1.0.0',
    'category': 'difmiadi',
    'author': 'Difference informatique - MIADI',
    
    'summary': 'Account update Miadi',
    'depends': [
        'base','base_setup', 'account', 'account_batch_payment'
    ],
    'data': [
        'views/inh_account_payment.xml',
        'views/inh_account_move_views.xml',
        #'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
