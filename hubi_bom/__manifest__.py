# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Bill of materials',
    'version': '2.0',
    'website': 'http://www.pole-erp-pgi.fr',
    'category': 'Sales/Sales',
    'sequence': 55,
    'summary': 'Bill of materials - BOMs',
    'author': 'Difference informatique - MIADI',
    'depends': ['product', 'stock', 'resource'],
    'description': "",
    'data': [
        'security/mrp_security.xml',
        'security/ir.model.access.csv',
        'views/mrp_bom_views.xml',
        'views/product_views.xml',
        
    ],
    'qweb': ['static/src/xml/*.xml'],
    'demo': [
        
    ],
    'test': [],
    'application': True,
    'license': 'OPL-1',
}
