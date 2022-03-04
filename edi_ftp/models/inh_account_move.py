# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class MiadiAccountMove(models.Model):
    _inherit = "account.move"

    di_transfer_edi = fields.Boolean(string='Transfer EDI', default=False) 
    
 