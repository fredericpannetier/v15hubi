# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import fields, models, api

class HubiPalSaleReportCarrier(models.Model):
    _inherit = "sale.report.carrier"
    
    pallet_number = fields.Integer(string = 'Number of pallet')

    def _selectC(self):
        #return super(HubiAccountInvoiceReport, self)._select()
        return super(HubiPalSaleReportCarrier, self)._selectC() + """,
            s.di_pallet_number as pallet_number
            """
   
    def _group_byC(self):
        return super(HubiPalSaleReportCarrier, self)._group_byC() + """,
                    s.di_pallet_number
                    
        """
       