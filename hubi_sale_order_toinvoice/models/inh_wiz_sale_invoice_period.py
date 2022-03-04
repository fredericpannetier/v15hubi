# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HubiCreatInvoicePeriod(models.Model):
    _inherit = "wiz.invoiceperiod"

    def invoice_create(self, sale_orders):
        res = super(HubiCreatInvoicePeriod, self).action_invoice_create(dateInvoice=self.invoice_date)
        for order in sale_orders:
            # Search the invoice
            invoices = self.env['account.move'].search([('invoice_origin', '=', order.name)])
            for invoice in invoices:
                if order.di_sending_date and not invoice.di_sending_date:
                    invoice.write({'di_sending_date': order.di_sending_date})

                if order.di_packaging_date and not invoice.di_packaging_date:
                    invoice.write({'di_packaging_date': order.di_packaging_date})

                if order.di_pallet_number and not invoice.di_pallet_number:
                    invoice.write({'di_pallet_number': order.di_pallet_number})

                if order.carrier_id.id and not invoice.di_carrier_id:
                    invoice.write({'di_carrier_id': order.carrier_id.id})
                    
                if order.di_comment and not invoice.di_comment:
                    invoice.write({'di_comment': order.di_comment})    