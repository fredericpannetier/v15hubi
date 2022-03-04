# -*- coding: utf-8 -*-
from odoo import models, fields, api, _,  SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import date, timedelta, datetime   
from itertools import groupby
import base64
#from ..controllers import ctrl_print
#from ...difmiadi_std.printing.controllers import ctrl_print

               
class MiadiSaleOrder(models.Model):
    _inherit = "sale.order"
    
    di_periodicity_invoice = fields.Selection(string="Invoice Period", related='partner_id.di_periodicity_invoice')#,store=True)
    di_invoice_grouping = fields.Boolean(string="Invoice grouping", related='partner_id.di_invoice_grouping')#,store=True)

    # @api.onchange("partner_id")
    # def di_onchange_partner_id(self):
    #     self.di_invoice_grouping = self.partner_id.di_invoice_grouping
    #     self.di_periodicity_invoice = self.partner_id.di_periodicity_invoice


    def action_invoice_create(self, grouped=False, final=False, dateInvoice=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        
        #inv_obj = self.env['account.move']
        #inv_lines = self.env['account.move.line']
        #references = {}
        
        #account_divers  = self.env['product.category'].search([('di_reference', 'in', ['D', 'd', 'DIVERS','Divers','divers',''] )], limit=1 ) 
        if not dateInvoice:
            date_invoices = time.strftime('%Y-%m-%d')
        else:
            date_invoices = dateInvoice 
               
        #date_due = False

        # 1) Create invoices.
        invoice_vals_list = []
        invoice_item_sequence = 0
        for order in self.sorted(key=lambda r: (r.partner_invoice_id.id, r.id)):
            order = order.with_company(order.company_id)
            current_section_vals = None
            down_payments = order.env['sale.order.line']

            inv_group = grouped
            if order.partner_invoice_id.di_invoice_grouping:
               #inv_group = False
               grouped= False
            else:
               #inv_group = True
               grouped = True
                   
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)

            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            invoice_lines_vals = []
            
            create_ent_bl = False
            if group_key not in invoices:
                    #inv_data = order._prepare_invoice()
                    #invoice = inv_obj.create(invoice_vals)
                    #references[invoice] = order
                    #invoices[group_key] = invoice
                    
                    create_ent_bl = True
                    
            elif group_key in invoices:
                    vals = {}
                    if order.name not in invoices[group_key].invoice_origin.split(', '):
                        vals['invoice_origin'] = invoices[group_key].invoice_origin + ', ' + order.name
                        create_ent_bl = True
                    if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(', ') and order.client_order_ref != invoices[group_key].name:
                        vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
                    invoices[group_key].write(vals)
                    
            if create_ent_bl:
                    #month = order.date_order.month 
                    #year = order.date_order.year
                    #day = order.date_order.day
                    #dateorder=datetime.strptime(order.date_order, '%d-%m-%Y')
                    #seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['statement_date']))
                    #dateorder=order.date_order.strftime('%d/%m/%Y')
                    dateorder=fields.Datetime.context_timestamp(self, order.date_order).strftime('%d/%m/%Y')
                    res = {
                        'display_type': 'line_section',    #'line_note', # False,
                        'sequence':invoice_item_sequence + 1,
                        'name': 'Cde no ' + order.name + ' du ' + dateorder,
                        #'move_name': order.name,
                        'product_id': False,
                        'product_uom_id': False,
                        'quantity': 0,
                        'discount': 0,
                        'price_unit': 0,
                        #'layout_category_id':  False,
                        #'account_id':  account_divers.property_account_income_categ_id.id or 630,
                        'tax_ids': False,
                        'analytic_account_id': False,
                        'analytic_tag_ids': False,
                        #'sale_line_ids': [(4, invoices[group_key].id)],

                    }
                    #
                    #res.update({'move_id': invoices[group_key].id })
                    #inv_lines |= self.env['account.move.line'].create(res)
                    
                    invoice_lines_vals.append(res)

            
            for line in order.order_line:
                if line.display_type == 'line_section':
                    current_section_vals = line._prepare_invoice_line(sequence=invoice_item_sequence + 1)
                    continue
                if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                    if line.is_downpayment:
                        down_payments += line
                        continue
                    if current_section_vals:
                        invoice_item_sequence += 1
                        invoice_lines_vals.append(current_section_vals)
                        current_section_vals = None
                    invoice_item_sequence += 1
                    prepared_line = line._prepare_invoice_line(sequence=invoice_item_sequence)
                    invoice_lines_vals.append(prepared_line)

            # If down payments are present in SO, group them under common section
            if down_payments:
                invoice_item_sequence += 1
                down_payments_section = order._prepare_down_payment_section_line(sequence=invoice_item_sequence)
                invoice_lines_vals.append(down_payments_section)
                for down_payment in down_payments:
                    invoice_item_sequence += 1
                    invoice_down_payment_vals = down_payment._prepare_invoice_line(sequence=invoice_item_sequence)
                    invoice_lines_vals.append(invoice_down_payment_vals)

            if not any(new_line['display_type'] is False for new_line in invoice_lines_vals):
                raise self._nothing_to_invoice_error()

            invoice_vals['invoice_line_ids'] = [(0, 0, invoice_line_id) for invoice_line_id in invoice_lines_vals]

            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise self._nothing_to_invoice_error()

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves


            
