# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiAccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'
    
    di_code = fields.Char(string='Code for the account')
