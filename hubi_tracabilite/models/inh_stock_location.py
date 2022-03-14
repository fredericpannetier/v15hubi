# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
   
class HubiTracabiliteLocation(models.Model):
    _inherit = "stock.location"
 
    di_storage = fields.Boolean('Authorized storage on this location', default=True)
    
