# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HubiInheritedResPartner(models.Model):
    _inherit = "res.partner"
       
    # EDI
    di_edi_invoice = fields.Boolean(string='EDI Invoice', default=False)
    di_edi_invoice_prod = fields.Boolean(string='EDI Invoice Production', default=False)
    di_edi_transport_recipient = fields.Char(string='EDI Transport Recipient')
    #di_order_code_ean = fields.Char(string='Order Code_EAN')
    #di_order_name = fields.Char(string='Order Name')
    di_code_ean = fields.Char(string='GLN Code')
    #CLAM - Ajout des champs
    di_code_ean_factor = fields.Char(string='EAN Factor Code')
    di_name_factor = fields.Char(string='Factor Name')
   