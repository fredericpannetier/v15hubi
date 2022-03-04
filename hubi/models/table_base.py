# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm, Warning

import logging

_logger = logging.getLogger(__name__)

"""
class HubiFamily(models.Model):
    _name = 'hubi.family'
    _description = "Product family"
    _order = 'name'
   
    
    def _get_level(self):
        level_vals = [("Caliber", "Caliber"),("Packaging", "Packaging")]
        return level_vals
  
    def _get_company_domain(self):    
        domain = [] 
        companies = self.env.user.company_ids  
        domain.append(('id', 'in', companies.ids))    
        return domain
    
#    @api.model
    def _get_company(self):
        return self.env.user.company_id
    
    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=_get_company, domain=lambda self: self._get_company_domain(), required=True)
    level = fields.Selection('_get_level', string="Level", Required=True, track_visibility=True )

    reference = fields.Char(string='Reference')
    default_value = fields.Boolean(string='Default Value', default=False)
    sale_ok = fields.Boolean(string='For Sale', default=True)
    purchase_ok = fields.Boolean(string='For Purchase', default=True)
    weight = fields.Float('Weight')
    

#    @api.multi
    @api.constrains('company_id')
    def _check_company(self):
        if (self.company_id not in self.env.user.company_ids): 
            raise ValidationError(_('The chosen company is not in the allowed companies for this family'))
"""
       
class HubiMultiTable(models.Model):
    _inherit = 'di.multi.table'
      
    def _get_record_type(self):
        vals = [("Caliber", "Caliber"),("Packaging", "Packaging"),("StockPackaging", "Stock Packaging")]
        return vals
    
    record_type = fields.Selection('_get_record_type', string="Level", Required=True, track_visibility=True )

    #reference = fields.Char(string='Reference')
    default_value = fields.Boolean(string='Default Value', default=False)
    sale_ok = fields.Boolean(string='For Sale', default=True)
    purchase_ok = fields.Boolean(string='For Purchase', default=True)
    weight = fields.Float('Weight')
    

       
