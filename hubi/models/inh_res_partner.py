# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from . import tools_hubi

class HubiInheritedResPartner(models.Model):
    _inherit = "res.partner"
   
    def _is_Visible(self):
        return tools_hubi._is_Visible_class(self, 'Partner')

    def _default_is_Visible(self, valeur):
        return tools_hubi._default_is_Visible_class(self, valeur) 
    
    def _default_family(self, valeur): 
        retour = 0
        option=self.env['di.multi.table']

        check_opt=option.search([('record_type','=', valeur)])
        for check in check_opt:
            if check.default_value:
                retour = check.id
        return retour
       
    def _get_default_company_id(self):
        return self._context.get('force_company', self.env.user.company_id.id)

    def _get_default_establishment(self):
        #default_establishment = self.env['ir.config_parameter'].sudo().get_param("hubi.di_default_establishment") or 0
        default_establishment = self.env['res.partner'].browse(int(self.env['ir.config_parameter'].sudo().get_param('hubi.di_default_establishment')))                
       
        return default_establishment
    
    """  
    @api.depends('customer_rank')
    def _is_customer(self):
        
        #Determine if the partner is a customer
        
        for record in self:
            if record.customer_rank != 0:
                record.di_is_customer = True
           
    def _is_supplier(self):
        
        #Determine if the partner is a supplier
        
        for record in self:
            if record.supplier_rank != 0:
                record.di_is_supplier = True
    """      

       
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=lambda self: self.env['res.country'].search([('code','=','FR')]))
    #di_family_type_id = fields.Many2one('di.multi.table', string='Type', domain=[('record_type', '=', 'Type')], help="The type of the partner.", default=lambda self: self._default_family('Type'))
    #di_family_job_id = fields.Many2one('di.multi.table', string='Job', domain=[('record_type', '=', 'Job')], help="The job of the partner.", default=lambda self: self._default_family('Job'))
    #di_family_id = fields.Many2one('di.multi.table', string='Family', domain=[('record_type', '=', 'Family')], help="The family of the partner.", default=lambda self: self._default_family('Family'))
    #di_cee_code = fields.Char(string='CEE Code')
 
    #di_remote_operation = fields.Boolean(string='Remote operation', default=False)
    #di_shipping = fields.Boolean(string='Shipping', default=False)
    #di_billing_fees = fields.Boolean(string='Billing fees', default=False) # Frais de facturation
    #di_frs_code = fields.Char(string='FRS Code')
    #di_ifls_code = fields.Char(string='IFLS Code')
    #di_ifls_edit_invoice = fields.Boolean(string='IFLS Edit Invoice', default=False)
    #di_ifls_edit_delivery = fields.Boolean(string='IFLS Edit Delivery', default=False)
    #di_ifls_edit_etiq = fields.Boolean(string='IFLS Edit Etiq', default=False)

    #di_carrier_id = fields.Many2one('delivery.carrier',string = 'Carrier')
    #di_price_list_id = fields.Integer(string = 'Price List')

    #di_red_label_number = fields.Char(string='Red Label Number')
    #di_cnuf = fields.Char(string='CNUF')

    # En-Tête
    #di_is_customer= fields.Boolean(string='Has a customer Invoice', default=False, store=True,  compute='_is_customer')
    #di_is_supplier= fields.Boolean(string='Has a supplier Invoice', default=False, store=True,  compute='_is_supplier')
    di_is_establishment = fields.Boolean(string='Is an establishment', default=False)

    # Caractéristique
    #di_sender_establishment = fields.Many2one('res.partner', string='Sender establishment', default=_get_default_company_id)
    di_sender_establishment = fields.Many2one('res.partner', string='Sender establishment',  domain=[('di_is_establishment', '=', True)] , default=_get_default_establishment )
    di_excluded_packaging = fields.Boolean(string='Excluded packaging', default=False)     # exclure des prévisions d'emballage
    
    di_asset = fields.Char(string='Asset')
    di_siret = fields.Char(string='Siret')
    di_rcs = fields.Char(string='RCS')
    di_naf = fields.Char(string='NAF')

    di_health_number = fields.Char(string='Health Number')
    
    # Gestion
    di_discount_invoice = fields.Float(string='Discount Invoice')
    di_discount_ca = fields.Float(string='Discount CA')
    di_discount_period_ca = fields.Selection([("Monthly", "Monthly"), ("Quarterly", "Quarterly"),
                              ("Annual", "Annual")], string="Period Discount CA")
    di_discount_description = fields.Char(string='CA Discount Description')
    #di_deb = fields.Boolean(string='DEB', default=False)
    
    #di_invoice_grouping = fields.Boolean(string='Invoice grouping', default=False)
    #di_periodicity_invoice = fields.Selection([("Daily", "Daily"),("Weekly", "Weekly"),("Decade", "Decade"),
    #                          ("Fortnight", "Fortnight"),("Monthly", "Monthly")], string="Invoice Period")

    # Impression
    di_product_grouping = fields.Boolean(string='Product grouping', default=False)
    di_valued_delivery = fields.Boolean(string='Valued delivery', default=False)   #BL Valorise
    di_bottom_message_invoice = fields.Text(string='Bottom message invoice')
    di_bottom_message_delivery = fields.Text(string='Bottom message delivery')

    #di_number_invoice = fields.Integer(string = 'Number Invoice', default=1)
    #di_number_delivery = fields.Integer(string = 'Number Delivery', default=1)
    #di_edit_price_kg = fields.Boolean(string='Edit price kg', default=False)
    #di_edit_weight = fields.Boolean(string='Edit weight', default=False)
    
    # Facturation
    di_amount_com_kg = fields.Float(string='Amount commission kg')  # Montant de la commission (achat)
    
    #di_auxiliary_account_customer = fields.Char(string='Auxiliary Account Customer')
    #di_auxiliary_account_supplier = fields.Char(string='Auxiliary Account Supplier')

    #di_over_credit = fields.Boolean('Allow Over Credit?', default=True)
    
    # EDI
#    di_edi_invoice = fields.Boolean(string='EDI Invoice', default=False)
#    di_edi_invoice_prod = fields.Boolean(string='EDI Invoice Production', default=False)
#    di_edi_transport_recipient = fields.Char(string='EDI Transport Recipient')
#    di_order_code_ean = fields.Char(string='Order Code_EAN')
#    di_order_name = fields.Char(string='Order Name')
    
    # Etiquette
    di_code_ean = fields.Char(string='GLN Code')
    di_customer_color_etiq = fields.Selection([("#FF00FF", "magenta"),("#0000FF", "blue"),
                                    ("#FFFF00", "yellow"),("#FF0000", "red"),
                                    ("#008000", "green"),("#D2691E", "brown"),
                                    ("#FFFFFF", "white"),("#CCCCCC", "grey"),
                                    ("#FFC0CB", "pink")], string='Customer Color Etiq') 
    di_customer_name_etiq = fields.Char(string='Customer Name Etiq')
    di_customer_city_etiq = fields.Char(string='Customer City Etiq')
    di_automatic_batch = fields.Boolean(string='Automatic Batch', default=False)   # No lot automatique
    di_ean128 = fields.Boolean(string='EAN128', default=False)
    di_code_ean128 = fields.Char(string='Start of barcode 128')
    di_compteur_ean128 = fields.Integer(string='Barcode 128 counter', default=0)

    di_dlc = fields.Boolean(string='DLC', default=False)
    di_dlc_number_day = fields.Integer(string = 'DLC Number Day')
    #di_type_etiq = fields.Selection([("1", "Etiquette Type 1"),("2", "Etiquette Type 2"),
    #                          ("3", "Etiquette Type 3")], string="Type Etiq")
    
    di_company_name_etiq = fields.Char(string='Company Name Etiq')
    di_company_city_etiq = fields.Char(string='Company City Etiq')
    di_etiq_model_id =  fields.Many2one('di.printing.etiqmodel', string='Etiquette model')
    di_etiq_printer = fields.Many2one('di.printing.printer', string='Etiquette Printer', domain=[('isimpetiq', '=', True)])
    di_etiq_mention = fields.Char(string='Etiq Mention')
    
    # Statistique
    di_statistics_alpha_1 = fields.Char(string='statistics alpha 1')
    di_statistics_alpha_2 = fields.Char(string='statistics alpha 2')
    di_statistics_alpha_3 = fields.Char(string='statistics alpha 3')
    di_statistics_alpha_4 = fields.Char(string='statistics alpha 4')
    di_statistics_alpha_5 = fields.Char(string='statistics alpha 5')
    di_statistics_num_1 = fields.Float(string='statistics numerical 1')
    di_statistics_num_2 = fields.Float(string='statistics numerical 2')
    di_statistics_num_3 = fields.Float(string='statistics numerical 3')
    di_statistics_num_4 = fields.Float(string='statistics numerical 4')
    di_statistics_num_5 = fields.Float(string='statistics numerical 5')
    
    #di_total_due = fields.Monetary(compute='_compute_total_due', string='Total Due')
    #di_total_overdue = fields.Monetary(compute='_compute_total_due', string='Total Overdue')
    
    #residual_aml_ids = fields.One2many('account.move.line', 'partner_id',
    #                                       domain=[
    #                                               ('move_id.payment_state', 'in', ('not_paid', 'partial')),
    #                                               ('move_id.state', '=', 'posted' )])
    
    #di_is_frs=fields.Boolean(string='is_FRS', compute='_is_Visible', default=lambda self: self._default_is_Visible('REF_FRS'))
    #di_is_ifls=fields.Boolean(string='is_IFLS', compute='_is_Visible', default=lambda self: self._default_is_Visible('GESTION_IFLS'))
    #di_is_edi_facture=fields.Boolean(string='is_EDI_FACTURE', compute='_is_Visible', default=lambda self: self._default_is_Visible('EDI_FACTURE'))
    #di_is_edi_transporteur=fields.Boolean(string='is_EDI_TRANSPORTEUR', compute='_is_Visible', default=lambda self: self._default_is_Visible('EDI_TRANSPORTEUR'))
    #di_is_bl_valorise=fields.Boolean(string='is_BL_VALORISE', compute='_is_Visible', default=lambda self: self._default_is_Visible('BL_VALORISE'))
    #di_is_etiq_lot_auto=fields.Boolean(string='is_ETIQ_LOT_AUTO', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_LOT_AUTO'))
    #di_is_prix_kg=fields.Boolean(string='is_PRIX_KG', compute='_is_Visible', default=lambda self: self._default_is_Visible('PRIX_KG'))
    #di_is_type_tiers=fields.Boolean(string='is_TYPE_TIERS', compute='_is_Visible', default=lambda self: self._default_is_Visible('TYPE_TIERS'))
    #di_is_etiq_dlc=fields.Boolean(string='is_ETIQ_DLC', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_DLC'))
    #di_is_etiq_couleur_client=fields.Boolean(string='is_ETIQ_COULEUR_CLIENT', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_COULEUR_CLIENT'))
    #di_is_etiq_ean_128=fields.Boolean(string='is_ETIQ_EAN_128', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_EAN_128'))
    #di_is_etiq_mode=fields.Boolean(string='is_ETIQ_MODE', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_MODE'))
    #di_is_etiq_type=fields.Boolean(string='is_ETIQ_TYPE', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_TYPE'))
    #di_is_export_compta=fields.Boolean(string='is_EXPORT_COMPTA', compute='_is_Visible', default=lambda self: self._default_is_Visible('EXPORT_COMPTA'))
    #di_is_fonction_deporte=fields.Boolean(string='is_FONCTION_DEPORTE', compute='_is_Visible', default=lambda self: self._default_is_Visible('FONCTION_DEPORTE'))
    #di_is_regr_prod_fac=fields.Boolean(string='is_REGR_PROD_FAC', compute='_is_Visible', default=lambda self: self._default_is_Visible('REGR_PROD_FAC'))
    
    """
        Compute the fields 'total_due', 'total_overdue'
    """
    """
    def _compute_total_due(self):
        
        
        today = fields.Date.context_today(self)
        for record in self:
            total_due = 0
            total_overdue = 0
           
            for aml in record.residual_aml_ids:
                if aml.company_id == self.env.company:
                    amount = aml.amount_residual
                    total_due += amount
                    is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                    if is_overdue and not aml.blocked:
                        total_overdue += amount
            record.di_total_due = total_due
            record.di_total_overdue = total_overdue
    """        
