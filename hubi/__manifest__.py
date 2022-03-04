# -*- coding: utf-8 -*-
{
    'name': 'HUBI',
    'version': '1.1',
    'summary': 'hubi',
    'category': 'Sales/Sales',
    'description': """
This module configures your application Hubi.
""",
    'author': 'Difference informatique - MIADI',
    'depends': [
        'base', 'base_setup', 'product', 'mail', 'sale', 'delivery', 'web', 'hubi_bom', 
        'hubi_menu', 'multi_table', 'tools', 'account_payment_mode','account_payment_partner', 'printing', 'hubi_printing', 'hubi_sale_order_toinvoice'#, 'hubi_edi_ftp' , 'hubi_palletization'
        
    ],
    'data': ["data/template_email.xml",
             'data/hubi_default_settings.xml',
        "views/inh_parameter_config_views.xml",
        "wizard/wiz_confirm_dialog_views.xml",
        "views/table_base_views.xml",
        "views/inh_product_template_views.xml",
        "wizard/wiz_create_productprice_views.xml",
        "views/inh_product_pricelist_views.xml",
        "views/inh_partner_views.xml",
        
        "views/inh_delivery_carrier_views.xml",
        
        "views/inh_account_invoice_views.xml",
        #"views/inh_account_payment_views.xml",
        "views/inh_packing_preparation_views.xml",
        "views/inh_sale_advance_payment_views.xml",
         
        "reports/partner_list_report.xml",
        "reports/partner_sheet_report.xml",
        "reports/productprice_sheet_report.xml",

        "reports/sale_order_report_views.xml",
        "reports/sale_order_hubi_report.xml",
        
        "reports/account_invoice_report_views.xml",
        "reports/account_invoice_summary_report.xml",
        "reports/account_invoice_hubi_report.xml",
        "reports/account_invoice_summary_report.xml",
        "reports/sale_carrier_report.xml",
        "reports/hubi_reports.xml",
             
        "wizard/wiz_create_product_from_category_views.xml",
        "wizard/wiz_search_product_views.xml", 
        "views/inh_sale_order_views.xml",
        "wizard/wiz_create_print_etiq_views.xml",
        "wizard/wiz_print_etiq_sale.xml",
        "wizard/wiz_sale_order_print_etiq_views.xml",
        "wizard/wiz_create_creditnote_ca_views.xml",
        
        
        
        "hubi_menu.xml",
        "security/hubi_security.xml",
        "security/ir.model.access.csv",
        #"data/res.country.state.csv"
        
        
    ],
    
    'demo': [#"data/res.country.department.xml",
             #"data/res.country.state.csv"
     ],
     
    'application': True,
    'license': 'OPL-1',
   
  
}
