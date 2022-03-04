# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
class WizCreateProductFromCategory(models.TransientModel):
    _name = "wiz.create.product.from.category"
    _description = "Wizard create products from the category"
    _order = 'categ_id, caliber_name, packaging_name'

    categ_id= fields.Integer('Category')
    caliber_id= fields.Integer('Caliber')
    packaging_id= fields.Integer('Packaging')
    caliber_name= fields.Char('Caliber Name')
    packaging_name= fields.Char('Packaging Name')
    categ_name= fields.Char('Category Name')
    categ_reference= fields.Char('Category Reference')
    caliber_reference= fields.Char('Caliber Reference')
    packaging_reference= fields.Char('Packaging Reference')

    weight = fields.Float(string='Weight')
    price = fields.Float( string='Default Price Unit')
    quantity = fields.Float( string='Quantity')
    account_income_id = fields.Many2one('account.account', string='Account Income')
    account_expense_id = fields.Many2one('account.account', string='Account Expense')
    etiq_printer = fields.Many2one('di.printing.printer', string='Etiquette Printer', domain=[('isimpetiq', '=', True)])
    packaging_sale_ok = fields.Boolean(string='For Sale', default=True)
    packaging_purchase_ok = fields.Boolean(string='For Purchase', default=True)
  

    @api.onchange('weight', 'price', 'quantity')
    def _onchange_input(self):
       weight_kg=self.weight or 0
       px=self.price or 0
       qte=self.quantity or 0
       origin_line = getattr(self, '_origin', self)
       self._cr.execute("UPDATE wiz_create_product_from_category SET  weight=%s , price=%s, quantity=%s WHERE id=%s", (weight_kg, px, qte, origin_line.id,))
       self.env.cr.commit()
       
    @api.onchange('etiq_printer')
    def _onchange_printer(self):
       if self.etiq_printer:
           label_printer=self.etiq_printer.id
       
           origin_line = getattr(self, '_origin', self)
           self._cr.execute("UPDATE wiz_create_product_from_category SET  etiq_printer=%s WHERE id=%s", (label_printer, origin_line.id,))
           self.env.cr.commit()       
        
#    @api.multi
    def create_product(self):
        #create the product from the category
        self.env.cr.commit()

        category = self.categ_id
        # default uom_id / uom_po_id
        uom_unit = self.env.ref('uom.product_uom_unit')
        uom_kg = self.env.ref('uom.product_uom_kgm')
        uom_unit_id = uom_unit.id
        uom_kg_id = uom_kg.id
        
        # default taxes
        #taxes_ref = self.env.ref('account.field_product_template_taxes_id')
        #taxes_supplier_ref = self.env.ref('account.field_product_template_supplier_taxes_id')
        
        taxe_id = 0
        #taxes  = self.env['ir.default'].search([('field_id', '=', taxes_ref.id),  ])
        #for taxe in taxes:
        #    taxe_id = taxes.json_value  

        taxe_supplier_id = 0
        #taxes_supplier  = self.env['ir.default'].search([('field_id', '=', taxes_supplier_ref.id),  ])
        #for taxe_supplier in taxes_supplier:
        #    taxe_supplier_id = taxes.json_value  

        #taxes = self.env['ir.default'].get('product.template', 'taxes_id')

        tax_ids=None
        #    'taxes_id': [(5, 0, 0)] if not tax_ids else [(6, 0, tax_ids)],
        #taxes_ids=False
        # 'taxes_id': [(6, 0, taxes_ids)],

        # ==== Taxes ====
        #self.tax_sale = self.company_data['default_tax_sale']
        #self.tax_purchase = self.company_data['default_tax_purchase']
        #'property_account_income_id': self.company_data['default_account_revenue'].id,
        #            'property_account_expense_id': self.company_data['default_account_expense'].id,
        #            'taxes_id': [(6, 0, self.tax_sale.ids)],
        #            'supplier_taxes_id': [(6, 0, self.tax_purchase.ids)],
         
        #taxe_id = self.env.company.account_sale_tax_id
        #taxe_supplier_id = self.env.company.account_purchase_tax_id
                    
        query_args = {'id_category': self.categ_id, 'id_user': self.env.user.id}
        query = """SELECT caliber_id, packaging_id, caliber_name, packaging_name, categ_name,
                    categ_reference, caliber_reference, packaging_reference, weight, price, quantity, etiq_printer,
                    account_income_id, account_expense_id, packaging_sale_ok, packaging_purchase_ok
                    FROM wiz_create_product_from_category 
                    WHERE categ_id=%(id_category)s AND create_uid=%(id_user)s AND weight<>0"""

        self.env.cr.execute(query, query_args)
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15] ) for r in self.env.cr.fetchall()]
            
        for caliber_id, packaging_id, caliber_name, packaging_name, categ_name, categ_reference, caliber_reference, packaging_reference, weight, price, quantity, etiq_printer, account_income_id, account_expense_id, packaging_saleok, packaging_purchaseok in ids:
            categ_ref = categ_reference or "" 
            caliber_ref = caliber_reference or "" 
            packaging_ref = packaging_reference or ""
            
            Ref_Interne_Component = categ_ref + caliber_ref
            Ref_Interne = categ_ref + caliber_ref + packaging_ref
            #Name_Product = packaging_name + '*' + categ_reference + caliber_reference
            Name_Product = categ_name + ' ' + caliber_name + ' x ' + packaging_name 
            Name_Interne_Component = categ_name + ' ' + caliber_name
            
            # Create Component product if it doesn't exist with this category, caliber
            id_tmpl_compo = 0  
            products_prod = self.env['product.template'].search([
                ('categ_id', '=', category),
                ('di_caliber_id', '=', caliber_id), 
                ('di_packaging_id', '=', False), 
                ('type', '=', 'product'), ])         
            for compo in products_prod:
                id_tmpl_compo = compo.id
            
            if id_tmpl_compo == 0: 
                # Create the product.template
                product_tmpl_compo_vals = {
                    'name': Name_Interne_Component,
                    'default_code': Ref_Interne_Component,
                    #'pallet_description': Ref_Interne_Component,
                    'weight': '0',
                    'di_quantity': '0',
                    'list_price': '0',
                    'categ_id': category,
                    'di_caliber_id': caliber_id,
                    'di_packaging_id': _(''),
                    'uom_id': uom_kg_id,
                    'uom_po_id': uom_kg_id,
                    'property_account_income_id': account_income_id,
                    'property_account_expense_id': account_expense_id,
                    #'taxes_id': taxe_id,
                    #'supplier_taxes_id': taxe_supplier_id,
                    #'taxes_id': [(5, 0, 0)] if not tax_ids else [(6, 0, tax_ids)],
                    #'supplier_taxes_id': [(5, 0, 0)] if not tax_ids else [(6, 0, tax_ids)],
                    
                    'purchase_ok': True,
                    'sale_ok': False,
                    'type': 'product',
                    'tracking': 'lot',
                     }
                product_tmpl_compo = self.env['product.template'].create(product_tmpl_compo_vals)
                id_tmpl_compo = product_tmpl_compo.id
            
            # Look for the id of the component in product.product
            products_prod_compo = self.env['product.product'].search([
                ('product_tmpl_id', '=', id_tmpl_compo),
                  ])         
            for prod_compo in products_prod_compo:
                id_compo = prod_compo.id
    
            # Create product if it doesn't exist with this category, caliber and packaging
            id_prod = 0  
            products_templ = self.env['product.template'].search([
            ('categ_id', '=', category),
            ('di_caliber_id', '=', caliber_id),
            ('di_packaging_id', '=', packaging_id), ])         
            for prod in products_templ:
                id_prod = prod.id
            
            if id_prod == 0: 
                # Create the product.template
                product_tmpl_vals = {
                    'name': Name_Product,
                    'default_code': Ref_Interne,
                    #'pallet_description': Name_Product,
                    'weight': weight,
                    'di_quantity': quantity,
                    'list_price': price,
                    'categ_id': category,
                    'di_caliber_id': caliber_id,
                    'di_packaging_id': packaging_id,
                    'uom_id': uom_unit_id,
                    'uom_po_id': uom_unit_id,
                    'property_account_income_id': account_income_id,
                    'property_account_expense_id': account_expense_id,
                    
                    #'taxes_id': taxe_id,
                    #'supplier_taxes_id': taxe_supplier_id,
                    #'taxes_id': [(5, 0, 0)] if not tax_ids else [(6, 0, tax_ids)],
                    #'supplier_taxes_id': [(5, 0, 0)] if not tax_ids else [(6, 0, tax_ids)],
                    
                    'purchase_ok': packaging_purchaseok,
                    'sale_ok': packaging_saleok,
                    'type': 'consu',
                    'tracking': 'none',
                    'di_etiq_printer': etiq_printer,
                     }
                product_tmpl = self.env['product.template'].create(product_tmpl_vals)

                # Create the product.product  --> automatic creation
                #product_vals = {
                #    'product_tmpl_id': product_tmpl.id,
                #    'default_code': Ref_Interne,
                #    'weight': weight,
                #     }
                #product = self.env['product.product'].create(product_vals)
            
                # Create the component mrp_bom
                mrp_bom_vals = {
                    'product_tmpl_id': product_tmpl.id,
                    'product_qty': '1',
                    'sequence': '0',
                    'product_uom_id': uom_unit_id,
                    'type': 'phantom',
                    'ready_to_produce':'asap',
                     }
                mrp_bom = self.env['mrp.bom'].create(mrp_bom_vals)
                                
                # Create the component mrp_bom_line
                mrp_bom_line_vals = {
                    'product_id': id_compo,
                    'product_qty': weight,
                    'product_uom_id': uom_kg_id,
                    'bom_id': mrp_bom.id,
                     }
                mrp_bom_line = self.env['mrp.bom.line'].create(mrp_bom_line_vals)

            self.env.cr.commit()
        
        self._cr.execute("DELETE FROM wiz_create_product_from_category WHERE categ_id=%s AND create_uid=%s", (self.categ_id, self.env.user.id))
        self.env.cr.commit()
        
        return {'type': 'ir.actions.act_window_close'}