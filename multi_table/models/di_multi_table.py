# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm, Warning

import logging

_logger = logging.getLogger(__name__)

class DiMultiTable(models.Model):
    _name = 'di.multi.table'
    _description = "Multi table"
    _order = 'name'
   
    
    def _get_record_type(self):
        # fonction à surcharger selon les besoins
        #voir pour permettre aux utilisateurs d'en rajouter
        vals = [("table", "Table")]
        return vals
  
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
    code = fields.Char(string='Code')
    record_type = fields.Selection('_get_record_type', string="Record type", required=True)    
    
    

#    @api.multi
    @api.constrains('company_id')
    def _check_company(self):
        if (self.company_id not in self.env.user.company_ids): 
            raise ValidationError(_('The chosen company is not in the allowed companies for this family'))
       
