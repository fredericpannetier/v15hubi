# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import api, fields, models, _

class DiPalletType(models.Model):
    _name = "di.pallet.type"
    _description = "Pallet Type"
    _order = "name"
    
    company_id = fields.Many2one('res.company', string='Company', readonly=True,  default=lambda self: self.env.user.company_id)             
    des = fields.Char(string="Description", required=True)
    name = fields.Char(string="Pallet Type", required=True)    
    
    @api.constrains('name')
    def _check_name(self):
        for tab in self:
            if tab.name:
                name = tab.search([('id', '!=', tab.id), ('name', '=', tab.name)], limit=1)
                if name:
                    raise ValidationError(_("Code is already used"))
                
class DiPalletProduct(models.Model):
    _name = "di.pallet.product"
    _description = "Pallet Product"
    _order = "name"
    
    company_id = fields.Many2one('res.company', string='Company', readonly=True,  default=lambda self: self.env.user.company_id)             
    name = fields.Char(string="Description", compute="_compute_name", store=True, readonly=True)
    pallet_type_id  = fields.Many2one('di.pallet.type', string="Pallet Type", required=True)
    product_id = fields.Many2one('product.product', 'Product' , store=True, compute='_comput_product_id')#   
    product_tmpl_id  = fields.Many2one('product.template', string='Product template')   #,  required=True
    #packaging_id = fields.Many2one(string='Packaging', comodel_name='ges.packaging', required=True)
    pack_num = fields.Integer(string='Packages number', required=True, help="""Number of packages per pallet""")
    
    @api.depends('pallet_type_id','product_tmpl_id')
    def _comput_product_id(self):
        for PalletP in self:
            if PalletP.pallet_type_id and PalletP.product_tmpl_id:
                PalletP.product_id = self.env['product.product'].search([('product_tmpl_id', '=', PalletP.product_tmpl_id.id)]).id
    
    @api.depends('pallet_type_id','product_id','product_tmpl_id')
    def _compute_name(self):
        for PalletP in self:
            if PalletP.pallet_type_id and PalletP.product_tmpl_id:
                PalletP.name = PalletP.pallet_type_id.name + '_' + PalletP.product_tmpl_id.default_code      
                
       
    @api.constrains('pallet_type_id','product_id','product_tmpl_id')
    def _check_name(self):
        for PalletP in self:
            if PalletP.pallet_type_id and PalletP.product_tmpl_id:
                name = PalletP.search([('id', '!=', PalletP.id), ('pallet_type_id', '=', PalletP.pallet_type_id.id), ('product_tmpl_id', '=', PalletP.product_tmpl_id.id)], limit=1)
                if name:
                    raise ValidationError(_("Already existing combination"))