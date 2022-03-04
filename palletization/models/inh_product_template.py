# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiProductPalletization(models.Model):
    _inherit = 'product.template'

    di_pallet_description = fields.Char(string='Pallet Description') 
    di_default_pallet_qty_1 = fields.Float(string='Default Quantity on the Pallet Type 1')
    di_default_pallet_qty_2 = fields.Float(string='Default Quantity on the Pallet Type 2')
    di_default_pallet_qty_3 = fields.Float(string='Default Quantity on the Pallet Type 3')
    
    di_pallet_type_1 = fields.Char(string='Pallet type 1' , compute='_compute_type_pallet_1')
    di_pallet_type_2 = fields.Char(string='Pallet type 2' , compute='_compute_type_pallet_2')
    di_pallet_type_3 = fields.Char(string='Pallet type 3' , compute='_compute_type_pallet_3')
    
    di_pallet_product_ids = fields.One2many('di.pallet.product', 'product_tmpl_id', string='Type pallet for this Product')
    
    def _compute_type_pallet_1(self):
        type_pallet_1 = self.env['ir.config_parameter'].sudo().get_param("palettization.di_pallet_type_1")
        #return type_pallet_1
        for line in self:
            line.update({
                'di_pallet_type_1': type_pallet_1,
            })

    def _compute_type_pallet_2(self):
        type_pallet_2 = self.env['ir.config_parameter'].sudo().get_param("palettization.di_pallet_type_2")
        for line in self:
            line.update({
                'di_pallet_type_2': type_pallet_2,
            })

    def _compute_type_pallet_3(self):
        type_pallet_3 = self.env['ir.config_parameter'].sudo().get_param("palettization.di_pallet_type_3")
        for line in self:
            line.update({
                'di_pallet_type_3': type_pallet_3,
            })
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    def get_pack_weight(self):
        return self.weight