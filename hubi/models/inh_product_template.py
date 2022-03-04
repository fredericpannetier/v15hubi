# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning, UserError, AccessError

from . import tools_hubi
import logging

_logger = logging.getLogger(__name__)

class HubiInheritedProductTemplate(models.Model):
    _inherit = "product.template"
    
    def _default_di_family(self, valeur): 
        retour = 0
        option=self.env['di.multi.table']
        if self.company_id.id:
            company = self.company_id.id
        else:
            company = self._context.get('force_company', self.env.user.company_id.id)
        check_opt=option.search([('record_type','=', valeur),('company_id', '=',company)])
        for check in check_opt:
            if check.default_value and retour == 0:
                retour = check.id
        return retour

    def _get_default_company_id(self):
        return self._context.get('force_company', self.env.user.company_id.id)


    company_id = fields.Many2one('res.company', string='Company', default=_get_default_company_id, required=True)

    di_caliber_id = fields.Many2one('di.multi.table', string='Caliber', domain=[('record_type', '=', 'Caliber')], help="The Caliber of the product.", default=lambda self: self._default_di_family('Caliber'))
    di_packaging_id = fields.Many2one('di.multi.table', string='Packaging', domain=[('record_type', '=', 'Packaging')], help="The Packaging of the product.", default=lambda self: self._default_di_family('Packaging'))
    di_quantity = fields.Float(string='Quantity')

    di_product_color = fields.Selection([("#FF00FF", "magenta"),("#0000FF", "blue"),
                                    ("#FFFF00", "yellow"),("#FF0000", "red"),
                                    ("#008000", "green"),("#D2691E", "brown"),
                                    ("#FFFFFF", "white"),("#CCCCCC", "grey"),
                                    ("#FFC0CB", "pink")], string='Product Color')    
    di_etiquette = fields.Boolean(string='Etiquette', default=False)

    di_etiq_printer = fields.Many2one('di.printing.printer', string='Etiquette Printer', domain=[('isimpetiq', '=', True)])
    di_etiq_model =  fields.Many2one('di.printing.etiqmodel', string='Etiquette model')

    di_etiq_mention = fields.Char(string='Etiquette Mention')
    di_etiq_description = fields.Char(string='Etiquette Description')
    di_etiq_latin = fields.Char(string='Etiquette Latin')
    di_etiq_spanish = fields.Char(string='Etiquette Spanish')
    di_etiq_english = fields.Char(string='Etiquette English')
    di_etiq_italian = fields.Char(string='Etiquette Italian')
    di_etiq_portuguese = fields.Char(string='Etiquette Portuguese')

    di_statistics_alpha_1 = fields.Char(string='Statistics alpha 1')
    di_statistics_alpha_2 = fields.Char(string='Statistics alpha 2')
    di_statistics_alpha_3 = fields.Char(string='Statistics alpha 3')
    di_statistics_alpha_4 = fields.Char(string='Statistics alpha 4')
    di_statistics_alpha_5 = fields.Char(string='Statistics alpha 5')
    
    def name_get(self):
 
        res = super(HubiInheritedProductTemplate, self).name_get()
        data = []
        for product in self:
            display_value = ''
            display_value += product.categ_id.display_name or ""
            display_value += ' / '
            display_value += product.di_caliber_id.name or ""
            display_value += ' / '
            display_value += product.di_packaging_id.name or ""
            display_value += ' / '
            display_value += product.name or ""
            display_value += '   ['
            display_value += product.default_code or ""
            display_value += ']'
            data.append((product.id, display_value))
        return data
    
    @api.onchange('di_packaging_id', 'di_caliber_id', 'categ_id')
    def _onchange_reference(self):

        refer = ""
        ref_pac = ""
        ref_cal = ""
        ref_cat = ""
                            
        try:
            if self.di_packaging_id and self.di_packaging_id.code: 
                ref_pac = self.di_packaging_id.code or ""
            if self.di_caliber_id and self.di_caliber_id.code:    
                ref_cal = self.di_caliber_id.code or ""
            if self.categ_id and self.categ_id.di_reference:    
                ref_cat = self.categ_id.di_reference or ""
            refer = ("%s%s%s") % (ref_cat, ref_cal, ref_pac)
            
        except Exception as e: 
            
            refer = ""
       
        self.default_code = refer
        
        if self.di_packaging_id.weight and self.weight==0: 
            self.weight = self.di_packaging_id.weight
            
    @api.onchange('barcode')
    def _onchange_barcode(self):
        # Test si code EAN13 correct
        #result = {}
        if self.barcode:
            if (len(self.barcode) < 12 or len(self.barcode) > 14):
                raise ValidationError("ERROR : Barcode EAN13. The length is invalid")
            else:
                cle_ean13 = self.env['di.tools'].calcul_cle_code_ean13(self.barcode)
                old_barcode = self.barcode
                deb_barcode = self.env['di.tools'].mid(self.barcode,0,12)
                self.barcode = deb_barcode + cle_ean13
                if (len(old_barcode) == 13) and (not cle_ean13 == old_barcode[12]):
                        #raise Warning(_('Barcode EAN13 invalid. The key is ' + cle_ean13))
                        raise UserError(_('Barcode EAN13 invalid. The key is ' + cle_ean13))
    
    def update_product_etiq(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        
        self.env.cr.commit()
        
        prod_compos = self.env['product.template'].browse(self._context.get('active_ids', []))
        for compo in prod_compos:
            # Search products from this category and caliber
            products=self.env['product.template'].search([
                ('categ_id', '=', compo.categ_id.id),
                ('di_caliber_id', '=', compo.di_caliber_id.id),
                ('di_packaging_id', '!=', False),    ])   
            for prod in products:
                if compo.di_etiq_printer and not prod.di_etiq_printer:   
                    prod.write({'di_etiq_printer':compo.di_etiq_printer})
                if compo.di_etiq_mention and not prod.di_etiq_mention:   
                    prod.write({'di_etiq_mention':compo.di_etiq_mention})    
                if compo.di_etiq_description and not prod.di_etiq_description:   
                    prod.write({'di_etiq_description':compo.di_etiq_description})  
                if compo.di_etiq_latin and not prod.di_etiq_latin:   
                    prod.write({'di_etiq_latin':compo.di_etiq_latin})  
                if compo.di_etiq_spanish and not prod.di_etiq_spanish:   
                    prod.write({'di_etiq_spanish':compo.di_etiq_spanish})     
                if compo.di_etiq_english and not prod.di_etiq_english:   
                    prod.write({'di_etiq_english':compo.di_etiq_english})     
                if compo.di_etiq_italian and not prod.di_etiq_italian:   
                    prod.write({'di_etiq_italian':compo.di_etiq_italian})     
                if compo.di_etiq_portuguese and not prod.di_etiq_portuguese:   
                    prod.write({'di_etiq_portuguese':compo.di_etiq_portuguese})     
                
                if compo.di_product_color and not prod.di_product_color:   
                    prod.write({'di_product_color':compo.di_product_color})     
                if compo.di_etiq_model and not prod.di_etiq_model:   
                    prod.write({'di_etiq_model':compo.di_etiq_model})     
                
                if compo.di_etiquette and not prod.di_etiquette:   
                    prod.write({'di_etiquette':compo.di_etiquette})    
        
        return {'type': 'ir.actions.act_window_close'}

    @api.constrains('company_id')
    def _check_company(self):
        if self.company_id:
            if (self.company_id not in self.env.user.company_ids): 
                raise ValidationError(_('The chosen company is not in the allowed companies for this product'))

class HubiInheritedProductCategory(models.Model):
    _inherit = "product.category"
    
    di_reference = fields.Char(string='Reference')
    di_shell = fields.Boolean(string='Shell', default=True)
    di_category_caliber_ids = fields.One2many('hubi.product_category_caliber', 'categ_id', string='Caliber for this category')
    di_nb_day_dluo = fields.Integer(string='Number day DLUO', default=0)

    def action_create_products(self):
        self.ensure_one()
        #return {}
        ir_model_data = self.env['ir.model.data']
        product_count = 0
        category_id = self.id
        account_income_id = self.property_account_income_categ_id.id
        account_expense_id = self.property_account_expense_categ_id.id
            
        #create  products from the category
        query_args = {'id_category' : self.id}
        
        self._cr.execute("DELETE FROM wiz_create_product_from_category WHERE categ_id=%s ", (self.id,))
        self.env.cr.commit()
        
        query = """SELECT categ_id, caliber_id, di_multi_table.id, 
                    caliber_family.name AS Name_Caliber, di_multi_table.name AS Name_Packaging, 
                    product_category.complete_name AS Name_Category,
                    product_category.di_reference AS Ref_Category, caliber_family.code AS Ref_Caliber, 
                    di_multi_table.code AS Ref_Packaging, di_multi_table.weight AS Weight_Packaging,
                    di_multi_table.sale_ok  AS SaleOK_Packaging, di_multi_table.purchase_ok  AS PurchaseOK_Packaging 
                    FROM hubi_product_category_caliber 
                    INNER JOIN product_category ON categ_id = product_category.id 
                    INNER JOIN di_multi_table AS caliber_family ON caliber_family.id = caliber_id  
                    , di_multi_table
                    WHERE di_multi_table.record_type='Packaging' AND categ_id=%(id_category)s
                    ORDER BY categ_id, caliber_family.name,  di_multi_table.name"""

        self.env.cr.execute(query, query_args)
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11]) for r in self.env.cr.fetchall()]
            
        for category, caliber, packaging, caliber_name, packaging_name, category_name, category_ref, caliber_ref, packaging_ref, packaging_weight, packaging_saleok, packaging_purchaseok in ids:
            # Product doesn't exist with this category, caliber and packaging
            id_prod = 0  
            products_templ = self.env['product.template'].search([
            ('categ_id', '=', self.id),
            ('di_caliber_id', '=', caliber),
            ('di_packaging_id', '=', packaging), ])         
            for prod in products_templ:
                id_prod = prod.id
            
            if id_prod == 0: 
                price_vals = {
                    'categ_id': category_id,
                    'caliber_id':caliber,
                    'packaging_id': packaging,
                    'caliber_name':caliber_name,
                    'packaging_name': packaging_name,
                    'categ_name':category_name,
                    'categ_reference':category_ref,                    
                    'caliber_reference':caliber_ref,
                    'packaging_reference': packaging_ref,
                    'account_income_id': account_income_id,
                    'account_expense_id': account_expense_id,
                        
                    'weight': packaging_weight,
                    #'weight':_('0'),
                    'price':'0',
                    'quantity':'0',  
                    'packaging_sale_ok':packaging_saleok,
                    'packaging_purchase_ok':packaging_purchaseok,        
                    }

                price = self.env['wiz.create.product.from.category'].create(price_vals)
                product_count = product_count + 1

        self.env.cr.commit()
        message_lib = ("%s %s %s %s ") % ("Create Product for category = (",self.id, ") ", self.name)
        
        #This function opens a window to create  products from the category
        try:
            create_product_form_id = ir_model_data.get_object_reference('hubi', 'create_product_from_category_form_view')[1]
            
        except ValueError:
            create_product_form_id = False
            
        try:
            search_view_id = ir_model_data.get_object_reference('hubi', 'create_product_from_category_search')[1]
            
        except ValueError:
            search_view_id = False
          
        ctx = {
            #'group_by':['category_id','di_caliber_id'],
            'default_model': 'product.category',
            'default_res_id': self.ids[0],
            'default_categ_id':category_id,
            'default_account_income_id':account_income_id,
            'default_account_expense_id':account_expense_id,
            'default_message':message_lib
            
        }
        domaine = [('categ_id', '=', category_id)]   
         
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [['categ_id', '=', self.id]],
            'res_model': 'wiz.create.product.from.category',
            #'src_model': 'product.category',
            'views': [(create_product_form_id, 'tree')],
            'view_id': create_product_form_id,
            'target': 'new',
            #'context': ctx
            
        }        

class HubiCategoryCaliber(models.Model):
    _name = "hubi.product_category_caliber"
    _description = "product category caliber"

    categ_id = fields.Many2one('product.category', string='Parent Category', index=True, ondelete='cascade')
    caliber_id = fields.Many2one('di.multi.table', string='Possible Caliber for this category', ondelete='cascade', index=True, domain=[('record_type', '=', 'Caliber')])

    _sql_constraints = [
        ('category_caliber_uniq', 'unique (categ_id,caliber_id)', 'The caliber must be unique per category !')
    ]
