# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import time
import calendar
from dateutil.relativedelta import relativedelta


class HubiSaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    invoice_date = fields.Date(string="Invoice Date", default=lambda self: fields.Date.today())

    #    @api.multi
    def create_invoices(self):
        context = dict(self.env.context)
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            #sale_orders.action_invoice_create(dateInvoice=self.invoice_date)
            sale_orders._create_invoices(date=self.invoice_date)
        elif self.advance_payment_method == 'all':
            #sale_orders.action_invoice_create(final=True, dateInvoice=self.invoice_date)
            sale_orders._create_invoices(final=True, date=self.invoice_date)
        else:
            #res = super(HubiSaleAdvancePaymentInv, self.with_context(context))._create_invoices()
            sale_orders._create_invoices(final=True, date=self.invoice_date)

        self.env.cr.commit()


        if self.advance_payment_method == 'delivered' or self.advance_payment_method == 'all':

            if not self.invoice_date:
                date_invoice = time.strftime('%Y-%m-%d')
            else:
                date_invoice = self.invoice_date

            date_due = False

            for order in sale_orders:
                # Search the invoice
                invoices = self.env['account.move'].search([('invoice_origin', '=', order.name)])
                for invoice in invoices:
                    if date_invoice:
                        invoice.write({'invoice_date': date_invoice})

                        # invoice.write({'invoice_date':invoice_date})
                        if invoice.invoice_payment_term_id:
                            #pterm = invoice.invoice_payment_term_id
                            #pterm_list = pterm.with_context(currency_id=invoice.company_id.currency_id.id).compute(value=1,
                            #                                                                          date_ref=date_invoice)[0]
                            #date_due = max(line[0] for line in pterm_list)
                            date_due =invoice.invoice_date_due
                        elif invoice.invoice_date_due and (date_invoice > invoice.invoice_date_due):
                            date_due = date_invoice

                    if date_due and not invoice.invoice_date_due:
                        invoice.write({'invoice_date_due': date_due})

                    if order.di_sending_date and not invoice.di_sending_date:
                        invoice.write({'di_sending_date': order.di_sending_date})

                    if order.di_packaging_date and not invoice.di_packaging_date:
                        invoice.write({'di_packaging_date': order.di_packaging_date})

                    if order.di_pallet_number and not invoice.di_pallet_number:
                        invoice.write({'di_pallet_number': order.di_pallet_number})

                    if order.di_comment and not invoice.di_comment:
                        invoice.write({'di_comment': order.di_comment})

                    if order.carrier_id.id and not invoice.di_carrier_id:
                        invoice.write({'di_carrier_id': order.carrier_id.id})



        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
        # return res

