# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm, Warning
from . import tools_hubi
   
class HubiProductPriceList(models.Model):
    _inherit = "product.pricelist"

    def _get_default_company_id(self):
        return self._context.get('force_company', self.env.user.company_id.id)
    
    company_id = fields.Many2one('res.company', string='Company',
        default=_get_default_company_id, required=True)

    di_shipping = fields.Boolean(string='Shipping', default=False)
    di_shipping_price_kg = fields.Float(string='Shipping Price Kg')
    
class HubiProductPriceListItem(models.Model):
    _inherit = "product.pricelist.item"
    
    #def _is_Visible(self):
    #    return tools_hubi._is_Visible_class(self, 'PriceList')

    #def _default_is_Visible(self, valeur):
    #    return tools_hubi._default_is_Visible_class(self,valeur) 

#    @api.one
    @api.depends('categ_id', 'product_tmpl_id', 'product_id', 'pricelist_id')
    def _get_pricelistitem_info(self):
        for px in self:
            if px.categ_id:
                px.di_info_price = _("") 
            elif px.product_tmpl_id:
                products_templ = px.env['product.template'].search([('id', '=', px.product_tmpl_id.id)])            
                price_kg = 0
            
                price_uom = px.env['uom.uom'].browse([products_templ.uom_id.id])
            
                if px.base == 'standard_price':
                    price = products_templ.standard_price
                else:    
                    price = products_templ.list_price
                convert_to_price_uom = (lambda price: products_templ.uom_id._compute_price(price, price_uom))

                if price is not False:
                    if px.compute_price == 'fixed':
                            price = convert_to_price_uom(px.fixed_price)
                    elif px.compute_price == 'percentage':
                            price = (price - (price * (px.percent_price / 100))) or 0.0
                    else:
                        # formula
                        price_limit = price
                        price = (price - (price * (px.price_discount / 100))) or 0.0
                        if px.price_round:
                            price = tools.float_round(price, precision_rounding=px.price_round)

                        if px.price_surcharge:
                            price_surcharge = convert_to_price_uom(px.price_surcharge)
                            price += price_surcharge

                        if px.price_min_margin:
                            price_min_margin = convert_to_price_uom(px.price_min_margin)
                            price = max(price, price_limit + price_min_margin)

                        if px.price_max_margin:
                            price_max_margin = convert_to_price_uom(px.price_max_margin)
                            price = min(price, price_limit + price_max_margin)
               
                    if products_templ.weight:
                        price_kg = price / products_templ.weight
                    
                px.di_info_price = ("%s %s %s %s %s %s %.2f %s %s %s") % (products_templ.di_quantity," ",products_templ.uom_id.name, ' - ',products_templ.weight," Kg - ", price_kg," ", self.currency_id.symbol," /Kg")
            elif px.product_id:
                px.di_info_price = _("")
            else:
                px.di_info_price = _("")
            
#    @api.one
    @api.depends('categ_id', 'product_tmpl_id', 'product_id', 'pricelist_id')
    def _get_di_default_price(self):
        if self.categ_id:
            self.di_default_price = '0'
        elif self.product_tmpl_id:
            products_templ=self.env['product.template']
            products_templ = self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)])            
            
            self.di_default_price = ("%s") % (products_templ.list_price)
        elif self.product_id:
            self.di_default_price = '0'
        else:
            self.di_default_price = '0'   

#    @api.one
    @api.depends('product_tmpl_id', 'product_id')
    def _get_di_weight(self):
        products_templ = self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)])            
        self.di_weight = ("%s") % (products_templ.weight)

#    @api.one
    def _compute_di_price_weight(self):
        for record in self:
            if record.di_weight != 0:
                record.di_price_weight = record.fixed_price / record.di_weight
            else:    
                record.di_price_weight = record.fixed_price
            record.di_price_weight = round(record.di_price_weight ,3)
        
#    @api.one
    def _compute_di_price_total(self):
        for record in self:
            if record.di_price_weight != 0:
                record.fixed_price = record.di_price_weight * record.di_weight
        
    @api.onchange('di_price_weight')
    def _onchange_di_price_weight(self):
        if (self.di_price_weight != 0) and (self.di_weight !=0):
            self.fixed_price = self.di_price_weight * self.di_weight        

        
    @api.onchange('fixed_price')
    def _onchange_price_total(self):
        if self.di_weight != 0:
            self.di_price_weight = self.fixed_price / self.di_weight
        else:    
            self.di_price_weight = self.fixed_price
        self.di_price_weight = round(self.di_price_weight ,3)
        


    @api.onchange('di_price_ean13')
    def _onchange_barcode(self):
        # Test si code EAN13 correct
        if self.di_price_ean13:
            if (len(self.di_price_ean13) < 12 or len(self.di_price_ean13) > 14):
                raise ValidationError("ERROR : Barcode EAN13. The length is invalid")
            else:
                cle_ean13 = self.env['di.tools'].calcul_cle_code_ean13(self.di_price_ean13)
                self.di_price_ean13 = self.env['di.tools'].mid(self.di_price_ean13,0,12) + cle_ean13


    #di_price_option = fields.Boolean(string='Price Option', default=False)
    di_price_color = fields.Selection([("#FF00FF", "magenta"),("#0000FF", "blue"),
                                    ("#FFFF00", "yellow"),("#FF0000", "red"),
                                    ("#008000", "green"),("#D2691E", "brown"),
                                    ("#FFFFFF", "white"),("#CCCCCC", "grey"),
                                    ("#FFC0CB", "pink")], string='Price Color')
    di_internal_code = fields.Char(string='Internal Code')
    di_price_ean13 = fields.Char(string='Price EAN13')
    #price_ifls = fields.Char(string='Price IFLS')
    di_customer_ref = fields.Char(string='Customer Ref')
    di_description_promo = fields.Char(string='Description Promo')
    di_price_printer =  fields.Many2one('di.printing.printer', string='Etiquette Printer', domain=[('isimpetiq', '=', True)])
    di_etiq_model_id = fields.Many2one('di.printing.etiqmodel', string='Etiquette model')

    #etiq_format = fields.Selection([("1", "large"),("2", "small"),("3", "weight"),("4", "other")], string="Etiq Format")
    #etiq_modele = fields.Selection([("1", "classic"),("2", "FD Taste of the quality"),
    #                                ("3", "Taste of the quality"),("4", "carton")], string="Etiq Modele")
   
    di_info_price = fields.Char('Info', compute='_get_pricelistitem_info',
        help="Information for this product (Quantity - Weight - Price weight")
    di_default_price = fields.Char('Default Price', compute='_get_di_default_price', help="Default price for this product.")
    di_weight = fields.Float(string='Weight for this product', compute='_get_di_weight')
    di_price_weight = fields.Float(string='Price Weight')

    #di_is_ifls=fields.Boolean(string='is_IFLS', compute='_is_Visible', default=lambda self: self._default_is_Visible('GESTION_IFLS'))
    #di_is_etiq_format=fields.Boolean(string='is_ETIQ_FORMAT', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_FORMAT'))
    #di_is_etiq_mode=fields.Boolean(string='is_ETIQ_MODE', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_MODE'))
    #di_is_tarif_option=fields.Boolean(string='is_TARIF_OPTION', compute='_is_Visible', default=lambda self: self._default_is_Visible('TARIF_OPTION'))
    #di_is_tarif_code_interne=fields.Boolean(string='is_CODE_INTERNE', compute='_is_Visible', default=lambda self: self._default_is_Visible('TARIF_CODE_INTERNE'))
    #di_is_tarif_ref_client=fields.Boolean(string='is_REF_CLIENT', compute='_is_Visible', default=lambda self: self._default_is_Visible('TARIF_REF_CLIENT'))
    #di_is_tarif_lib_promo=fields.Boolean(string='is_LIB_PROMO', compute='_is_Visible', default=lambda self: self._default_is_Visible('TARIF_LIB_PROMO'))
