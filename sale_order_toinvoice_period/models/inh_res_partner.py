# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class MiadiInheritedResPartner(models.Model):
    _inherit = "res.partner"
    
    di_invoice_grouping = fields.Boolean(string='Invoice grouping', default=False)
    di_periodicity_invoice = fields.Selection([("Daily", "Daily"),("Weekly", "Weekly"),("Decade", "Decade"),
                              ("Fortnight", "Fortnight"),("Monthly", "Monthly")], string="Invoice Period")
