# See LICENSE file for full copyright and licensing details.

{
    'name': 'Palletization',
    'version': '14.0.1.0.0',
    'category': 'difmiadi',
    'author': 'Difference informatique - MIADI',
    
    'summary': 'Palletization',
    'depends': [
        'base','base_setup','sale','delivery'
    ],
    'data': [
        'data/pallet_default_settings.xml',
        'views/type_pallet_views.xml',
        'views/inh_res_partner_views.xml',
        'views/inh_res_company_views.xml',
        'views/inh_parameter_config_views.xml',
        'views/palletization_views.xml',
        'views/inh_product_template_views.xml',
        'reports/reports_pallet.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
