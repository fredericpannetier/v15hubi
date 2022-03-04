# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
#from odoo import models, fields, api, _
   
class HubiDeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"
    _description = "delivery.carrier"

    di_agency_number = fields.Char(string='Agency Number')
    di_agency_city = fields.Char(string='Agency City') 
    di_street = fields.Char(string='Street')
    di_street2 = fields.Char(string='Street 2')
    di_city = fields.Char(string='City')
    di_zip = fields.Char(string='Zip')
    di_department =  fields.Many2one('res.country.state', string='Department', domain=[('country_id.code', '=', 'FR')])
    di_contact_name = fields.Char(string='Contact Name')
    di_phone = fields.Char(string='Phone')
    di_mobile = fields.Char(string='Mobile')
    di_fax = fields.Char(string='Fax')
    di_mail = fields.Char(string='Mail')
    di_account = fields.Char(string='Account')
    di_recipient = fields.Char(string='Recipient')
    di_color_carrier = fields.Selection([("#FF00FF", "magenta"),("#0000FF", "blue"),
                                    ("#FFFF00", "yellow"),("#FF0000", "red"),
                                    ("#008000", "green"),("#D2691E", "brown"),
                                    ("#FFFFFF", "white"),("#CCCCCC", "grey"),
                                    ("#FFC0CB", "pink")], string='Carrier Color Etiq') 