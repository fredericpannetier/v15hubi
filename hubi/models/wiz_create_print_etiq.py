# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import time
import calendar
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
#from ..controllers import ctrl_print
#from ...difmiadi_std.printing.controllers import ctrl_print
from . import tools_hubi

class Wizard_create_print_etiq(models.TransientModel):
    _name = "wiz_create_print_etiq"
    _description = "Wizard creation of a etiquette and print it"
    
    @api.onchange('category_id', 'caliber_id', 'packaging_id')
    def _onchange_product_ccp(self):
        product_domain = [('sale_ok','=',True),('di_etiquette', '=', True)]
        
        if self.category_id:
            product_domain = [('categ_id', '=', self.category_id.id)]+ product_domain[0:]
        if self.caliber_id:
            product_domain = [('di_caliber_id', '=', self.caliber_id.id)] + product_domain[0:]
        if self.packaging_id:
            product_domain = [('di_packaging_id', '=', self.packaging_id.id)] + product_domain[0:]
            
        if self.category_id  and self.caliber_id  and self.packaging_id:
            # Recherche de l'article en fonction des sélections 
            id_prod = 0  
            products_templ = self.env['product.template'].search([
            ('categ_id', '=', self.category_id.id),
            ('di_caliber_id', '=', self.caliber_id.id),
            ('di_packaging_id', '=', self.packaging_id.id), ])         
            for prod in products_templ:
                id_prod = prod.id
                
            if id_prod != 0:
                # search the code in product.product
                products_prod_prod = self.env['product.product'].search([
                ('product_tmpl_id', '=', id_prod),  ])         
                for prod_prod in products_prod_prod:
                    id_prod_prod = prod_prod.id

                self.product_id = id_prod_prod 
       
        return {'domain': {'product_id': product_domain}}

    @api.onchange( 'partner_id')
    def _onchange_partner(self):
        self.carrier_id = None
        if self.partner_id:
           self.carrier_id = self.partner_id.property_delivery_carrier_id 
            
    @api.onchange('product_id', 'partner_id')
    def _onchange_partner_product(self):
        self.pds = None
        self.nb_mini = None 
        self.color_etiq = None
        self.code_barre = None
        self.printer_id =  None 
        self.model_id = None
        self.etabexp_id = None
        self.health_number = None 
        self.code_128 = None 
        
        
        if self.partner_id:
            # Recherche de l'établissement expéditeur 
            id_partner_sender = 0 
            codbar_128 = ""    
            partner_sender = self.env['res.partner'].search([('id', '=', self.partner_id.di_sender_establishment.id), ])         
            for sender in partner_sender:
                id_partner_sender = sender.id
                health_no = sender.di_health_number
                if (not sender.di_compteur_ean128) or (sender.di_compteur_ean128==0):
                    compt_ean128 = 1
                else:
                    compt_ean128 = sender.di_compteur_ean128
                     
            if id_partner_sender != 0:
                self.etabexp_id = id_partner_sender
               #if not self.health_number: 
                self.health_number = health_no           
                if self.partner_id.di_ean128:
                    if sender.di_code_ean128:
                        codbar_128 = ("%s%08d") % (sender.di_code_ean128, compt_ean128)
                        self.code_128 = codbar_128
           
            color_partner = self.partner_id.di_customer_color_etiq
            printer_partner = self.partner_id.di_etiq_printer
            modele_partner = self.partner_id.di_etiq_model_id
             
            
        if (self.product_id) and (self.partner_id):
            color_prod = self.product_id.di_product_color
            code_barre_prod = self.product_id.barcode
            printer_prod = self.product_id.di_etiq_printer
            modele_prod = self.product_id.di_etiq_model
            weight_prod = self.product_id.weight
            number_prod = self.product_id.di_quantity

                # search the code in product.product
                #products_prod_prod = self.env['product.product'].search([('product_tmpl_id', '=', id_prod),  ])         
                #for prod_prod in products_prod_prod:
                #    id_prod_prod = prod_prod.id
                #    color_prod = prod_prod.di_product_color
                #    code_barre_prod = prod_prod.barcode
                #    printer_prod = prod_prod.di_etiq_printer
                #    modele_prod = prod_prod.di_etiq_model
                #    weight_prod = prod_prod.weight
                #    number_prod = prod_prod.di_quantity
                
            # Recherche du tarif de l'article        
            id_partner_price = 0  
            partner_price = self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', self.partner_id.property_product_pricelist.id),
                    ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
                     ])         
            for price in partner_price:
                id_partner_price = price.id
                
                color_price = price.di_price_color
                code_barre_price = price.di_price_ean13
                printer_price = price.di_price_printer
                modele_price = price.di_etiq_model_id   
            
            self.pds = weight_prod
            self.nb_mini = number_prod   
              
            # Priorité 1 : Tarif
            if id_partner_price != 0:
                    self.color_etiq = color_price
                    self.code_barre = code_barre_price
                    self.printer_id =  printer_price 
                    self.model_id = modele_price
                
            if not self.color_etiq:
                if color_prod:
                    self.color_etiq = color_prod
                elif color_partner:
                    self.color_etiq = color_partner  

            if not self.code_barre:    
                    self.code_barre = code_barre_prod 
 
            default_value = self.env['di.printing.parameter'].search([('name', '=ilike', 'DEFAULT')])
            for default in default_value:
                default_printer = default.printer_id.id
                default_etiq = default.etiquette_model_id.id
                           
            if not self.printer_id:
                if printer_prod:
                    self.printer_id =  printer_prod 
                elif printer_partner:
                    self.printer_id = printer_partner     
                elif default_printer:
                    self.printer_id = default_printer
                    
            if not self.model_id:    
                #Priorité 2 = client
                if modele_partner:
                    self.model_id =  modele_partner 
                elif modele_prod:
                    self.model_id = modele_prod    
                elif default_etiq:
                    self.model_id = default_etiq
                    
    @api.depends('product_id', 'packaging_date', 'partner_id')
    def _compute_dluo(self):
        if self.packaging_date and self.product_id.id:
            if self.partner_id.di_dlc_number_day and self.partner_id.di_dlc_number_day>0:
                val_nb_day=self.partner_id.di_dlc_number_day
            else:    
                val_nb_day=self.product_id.categ_id.di_nb_day_dluo or 7
            val_calcul_dluo = fields.Date.from_string(self.packaging_date) + timedelta(days=val_nb_day)
            self.date_dluo = val_calcul_dluo
               
    packaging_date = fields.Date(string="Packaging date",default=lambda self: fields.Date.today())
    sending_date = fields.Date(string="Sending date",default=lambda self: fields.Date.today())
    caption_etiq = fields.Char(string="Caption etiquette")
    product_id = fields.Many2one('product.product', string='Product')
    #product_name = fields.Char(string="Product")
    #caliber_name = fields.Char(string="Caliber")
    #packaging_name = fields.Char(string="Packaging")
    category_id = fields.Many2one('product.category', 'Internal Category', domain=[('parent_id','!=',False), ('di_shell', '=', True)], store=False)
    caliber_id = fields.Many2one('di.multi.table', string='Caliber', domain=[('record_type', '=', 'Caliber')], help="The Caliber of the product.", store=False)
    packaging_id = fields.Many2one('di.multi.table', string='Packaging', domain=[('record_type', '=', 'Packaging')], help="The Packaging of the product.", store=False)

    code_barre = fields.Char(string="Bar Code")
    code_128 = fields.Char(string="Bar Code 128")
    qte = fields.Float(string="Quantity", default = 1)
    pds = fields.Float(string="Weight", default = 0)
    numlot = fields.Char(string="Batch number")
    nb_mini = fields.Float(string="Minimum number", default = 0)
    health_number = fields.Char(string='Health Number')
    partner_id = fields.Many2one("res.partner", string='Customer')
    etabexp_id = fields.Many2one("res.partner", string='Sender establishment')
    printer_id = fields.Many2one("di.printing.printer", string='Etiquette Printer', domain=[('isimpetiq', '=', True)])
    model_id = fields.Many2one("di.printing.etiqmodel", string='Etiquette Model')
    color_etiq = fields.Selection([("#FF00FF", "magenta"),("#0000FF", "blue"),
                                    ("#FFFF00", "yellow"),("#FF0000", "red"),
                                    ("#008000", "green"),("#D2691E", "brown"),
                                    ("#FFFFFF", "white"),("#CCCCCC", "grey"),
                                    ("#FFC0CB", "pink")], string='Color Etiq')
    #carrier_id = fields.Integer(string="Carrier ID")
    carrier_id = fields.Many2one('delivery.carrier', 'Carrier ID')
    date_dluo = fields.Date(string="DLUO Date", store=True, compute='_compute_dluo')
    message = fields.Text(string="Information")
   
 
#    @api.multi
    def create_print_etiq(self):  
        self.env.cr.commit()
        no_id = self.id
        nom_table = "wiz_create_print_etiq"
        tools_hubi.prepareprintetiq(self, nom_table, no_id)
        return {'type': 'ir.actions.act_window_close'} 
            