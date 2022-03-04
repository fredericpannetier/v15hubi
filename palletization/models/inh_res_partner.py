# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
   
class MiadiResPartner(models.Model):
    _inherit = "res.partner"
    
    di_cnuf = fields.Char(string='CNUF')