# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
   
class MiadiDeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"
    
    di_cnuf = fields.Char(string='CNUF')