# See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Order to Invoice Period',
    'version': '14.0.1.0.0',
    'category': 'difmiadi',
    'author': 'Difference informatique - MIADI',
    'description': """
        This module allows you to group sales orders to invoices
    """,
    'summary': 'Sale Order to Invoice Period',
    'depends': [
        'base','base_setup','sale',
    ],
    'data': ['views/inh_partner_views.xml',
        'wizard/wiz_sale_invoice_period_views.xml',
        
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
