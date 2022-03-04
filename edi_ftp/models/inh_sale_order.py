# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class MiadiSaleOrder(models.Model):
    _inherit = "sale.order"

    di_transfer_edi = fields.Boolean(string='Transfer EDI', default=False) 
    
 