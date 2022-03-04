# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
   
class MiadiResCompany(models.Model):
    _inherit = "res.company"
   
    di_cnuf = fields.Char(related='partner_id.di_cnuf', string="CNUF", readonly=False)  # , inverse="_inverse_di_cnuf"
    
    #@api.model
    #def create(self, vals):
    
    def _inverse_di_cnuf(self):
        for company in self:
            company.partner_id.di_cnuf = company.di_cnuf

        