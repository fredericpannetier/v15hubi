# -*- coding: utf-8 -*-
from odoo import models, fields, api, _,  SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import date, timedelta, datetime   
from itertools import groupby
import base64
#from nntplib import lines
#from ..controllers import ctrl_print
#from ...difmiadi_std.printing.controllers import ctrl_print

class HubiSaleOrderLine(models.Model):
    _inherit = "sale.order.line"
       
    @api.onchange('di_category_id', 'di_caliber_id', 'di_packaging_id')
    def _onchange_product(self):
        product_domain = [('sale_ok','=',True)]
        
        if self.di_category_id:
            product_domain = [('categ_id', '=', self.di_category_id.id)]+ product_domain[0:]
        if self.di_caliber_id:
            product_domain = [('di_caliber_id', '=', self.di_caliber_id.id)] + product_domain[0:]
        if self.di_packaging_id:
            product_domain = [('di_packaging_id', '=', self.di_packaging_id.id)] + product_domain[0:]
            
        if self.di_category_id  and self.di_caliber_id  and self.di_packaging_id:
            # Recherche de l'article en fonction des sélections 
            id_prod = 0  
            products_templ = self.env['product.template'].search([
            ('categ_id', '=', self.di_category_id.id),
            ('di_caliber_id', '=', self.di_caliber_id.id),
            ('di_packaging_id', '=', self.di_packaging_id.id), ])         
            for prod in products_templ:
                id_prod = prod.id

            #self.env.cr.execute('SELECT id FROM product_template '
            #            'WHERE di_categ_id = %s AND caliber_id = %s AND di_packaging_id = %s  ',
            #            (self.category_id.id, self.caliber_id.id, self.di_packaging_id.id))
            #res = self.env.cr.fetchone()
            #if res:
            #   id_prod = res[0]
                
            if id_prod != 0:
                # search the code in product.product
                products_prod_prod = self.env['product.product'].search([
                ('product_tmpl_id', '=', id_prod),  ])         
                for prod_prod in products_prod_prod:
                    id_prod_prod = prod_prod.id
                    
                self.product_id = id_prod_prod    
        
        return {'domain': {'product_id': product_domain}}

    @api.depends('product_uom_qty', 'price_total', 'product_id', 'order_id')
    def _compute_weight(self):
        """
        Compute the weights of the Sale Order lines.
        """
        for line in self:
            factor = line.product_uom.factor * line.product_id.uom_id.factor
            if factor != 0: 
                weight = line.product_id.weight * (line.product_uom_qty / factor)
            else:
                weight = line.product_id.weight * line.product_uom_qty  
            weight = round(weight,3)
                     
            if weight!=0:
                if line.discount >= 100: 
                    price_weight = (line.price_unit * line.product_uom_qty) / weight                          
                else:  
                    price_weight = line.price_subtotal / weight
            else:   
                price_weight = 0
               
            price_weight = round(price_weight ,3)   
            
            line.update({
                'di_weight': weight,
                'di_price_weight': price_weight
                
            })
            

    @api.depends('order_id', 'product_id', 'order_id.di_packaging_date', 'order_partner_id')
    def _compute_dluo(self):
        for line in self:
            if line.order_id.di_packaging_date and line.product_id.id:
                if line.order_partner_id.di_dlc_number_day and line.order_partner_id.di_dlc_number_day>0:
                    val_nb_day=line.order_partner_id.di_dlc_number_day
                else:    
                    val_nb_day=line.product_id.categ_id.di_nb_day_dluo or 7
                val_calcul_dluo = fields.Date.from_string(line.order_id.di_packaging_date) + timedelta(days=val_nb_day)
                
                line.update({
                'di_date_dluo': val_calcul_dluo
                })

    
    @api.onchange('product_id')
    def product_change(self):
        if self.product_id.id:
            super(HubiSaleOrderLine, self).product_uom_change()
            """
            # Batch number
            if not self.di_no_lot:
                _nolot = ''
                if self.order_id.di_sending_date:
                    val_calcul_lot = self.order_id.di_calcul_lot 
                    dateAAAAMMJJ=fields.Date.from_string(self.di_sending_date).strftime('%Y%m%d')
                    dateQQQ=fields.Date.from_string(self.di_sending_date).strftime('%Y%j')
        
                    if val_calcul_lot=='AQ': 
                        _nolot = dateQQQ
                    else:
                        if val_calcul_lot=='AMJ': 
                            _nolot = dateAAAAMMJJ

                self.di_no_lot = _nolot
            """

    @api.onchange('price_unit')
    def price_change(self):
        if self.product_id.id and self.price_unit == 0:
                #raise UserError(_('Error in the price. The value is 0.'))
                title = ("Warning for %s") % self.product_id.name
                message = 'Error in the price. The value is 0.'
                warning = {
                    'title': title,
                    'message': message, }
                return {'warning': warning}
            
            
    di_category_id = fields.Many2one('product.category', 'Internal Category', domain=[('parent_id','!=',False), ('di_shell', '=', True)], store=False)
    di_caliber_id = fields.Many2one('di.multi.table', string='Caliber', domain=[('record_type', '=', 'Caliber')], help="The Caliber of the product.", store=False)
    di_packaging_id = fields.Many2one('di.multi.table', string='Packaging', domain=[('record_type', '=', 'Packaging')], help="The Packaging of the product.", store=False)
    di_weight = fields.Float(string='Weight ', store=True, readonly=True, compute='_compute_weight')
    di_price_weight = fields.Float(string='Price Weight ', store=True, readonly=True, compute='_compute_weight')
    di_commentary = fields.Char(string='Commentary')
    
    di_no_lot = fields.Char(string='Batch number')
    partner_id = fields.Many2one("res.partner", string='Customer')
    di_done_packing = fields.Boolean(string='Packing Done')
    di_sending_date = fields.Date(string="Sending Date", store=False, compute='_compute_date_sending' )
    di_date_dluo = fields.Date(string="DLUO Date",store=True, compute='_compute_dluo')   
    di_etiquette_product = fields.Boolean(string="Product label", related='product_id.di_etiquette')
   
    
    
#    @api.multi
    def invoice_line_create(self, move_id, qty):
        #invoice_line_vals = super(HubiSaleOrder, self)._prepare_invoice_line(qty=qty)
        invoice_line_vals = super(HubiSaleOrderLine, self).invoice_line_create(move_id, qty)
        invoice_line_vals.update({
            'di_commentary': self.di_commentary,
            #'di_weight': self.di_weight,
            #'di_weight_signed': self.di_weight,
            #'di_price_weight': self.di_price_weight,
            #'di_no_lot': self.di_no_lot
        })
        return invoice_line_vals  
  
     
#    @api.multi
    def print_etiq(self):
        #self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        #return self.env.ref('hubi.report_orderline_label').report_action(self)
        ##return {'type': 'ir.actions.report','report_name': 'report_saleorder_hubi_document','report_type':"qweb-pdf"}
        sale_order_ids = self.env['wiz_sale_order_print_etiq'].browse(self.id)
        res = sale_order_ids.load_order_line('order_line')
        
        if len(res) >= 1:
            action = self.env.ref('hubi.action_wiz_sale_order_print_etiq_tree').read()[0]
            action['domain'] = [('id', 'in', res)]
            
        return action
    
#   @api.multi
    def validation(self):
        #Lorsque l'on appuie sur le bouton, la ligne n'est plus affichée sur la page
        for line in self:
            line.update({
                'di_done_packing': True,
                #'di_packaging_date':fields.Date.context_today(self),

            })
        return
 
#    @api.multi
    def _compute_date_sending(self):
        for line in self:
            #line.sending_date = line.order_id.sending_date
            line.update({
                'di_sending_date': line.order_id.di_sending_date,
                
            })
               
class HubiSaleOrder(models.Model):
    _inherit = "sale.order"

#    @api.multi
    def action_search_products(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        product_count = 0
        sale_order_id = self.id
        #create  products depending on the pricelist
        query_args = {'pricelist_code': self.pricelist_id.id,'date_order' : self.date_order,'id_order' : self.id}
        
        self._cr.execute("DELETE FROM wiz_search_product_line WHERE order_line_id=%s AND pricelist_line_id=%s", (self.id,self.pricelist_id.id,))
        self.env.cr.commit()
        
        prod_prec = ''
        query = """Select product_product.id, date_start, date_end, product_category.complete_name, di_multi_table.name, 
                    case compute_price when 'fixed' then fixed_price else list_price*(1-percent_price/100) end as Price,
                    case when  date_start is null then '01/01/1900' ELSE date_start END as date_debut, min_quantity 
                    from product_pricelist_item
                    inner join product_template on product_pricelist_item.product_tmpl_id=product_template.id
                    inner join product_product on product_product.product_tmpl_id=product_template.id
                    inner join product_category on product_template.categ_id = product_category.id
                    inner join di_multi_table on product_template.di_caliber_id = di_multi_table.id
                    where (pricelist_id= %(pricelist_code)s ) and (product_pricelist_item.product_tmpl_id is not null) 
                    and (date_start<=%(date_order)s  or date_start is null)
                    and (date_end>=%(date_order)s  or date_start is null)
                    AND (product_product.id NOT IN (SELECT product_id FROM sale_order_line WHERE order_id=%(id_order)s))
                    order by product_product.id, date_debut desc, min_quantity """

        self.env.cr.execute(query, query_args)
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]) for r in self.env.cr.fetchall()]
            
        for product, date_start, date_end, category, caliber, unit_price, date_debut, qty in ids:
            if product != prod_prec:
                price_vals = {
                    'order_line_id': sale_order_id,
                    'pricelist_line_id':self.pricelist_id.id,
                    'product_id': product,
                    'qty_invoiced':'0',
                    'price_unit':unit_price,
                    'date_start': date_start,
                    'date_end': date_end, 
                    'category_id': category,
                    'caliber_id': caliber,               
                    }

                price = self.env['wiz.search.product.line'].create(price_vals)
                product_count = product_count + 1
                prod_prec = product

        self.env.cr.commit()
        message_lib = ("%s %s %s %s ") % ("Create Product for price list = (",self.pricelist_id.id, ") ", self.pricelist_id.name)
        
        #This function opens a window to create  products depending on the pricelist
        try:
            search_product_form_id = ir_model_data.get_object_reference('hubi', 'Price_List_Lines_form_view')[1]
            
        except ValueError:
            search_product_form_id = False
            
        try:
            search_view_id = ir_model_data.get_object_reference('hubi', 'Price_List_Lines_search')[1]
            
        except ValueError:
            search_view_id = False
          
        ctx = {
            #'group_by':['category_id','caliber_id'],
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_order_line_id':self.id,
            'default_pricelist_line_id':self.pricelist_id.id
            ,'default_message':message_lib
            
        }
        dom = [
            ('order_line_id', '=', sale_order_id),
            ('pricelist_line_id', '=', self.pricelist_id.id)
        ]   
         
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'wiz.search.product.line',
            'views': [(search_product_form_id, 'tree')],
            'view_id': search_product_form_id,
            'search_view_id': search_view_id,
            #'target': 'inline',
            'target': 'new',
            'context': ctx,
            'domain':dom,
        }
    
     
#    @api.multi
    def action_print_etiq(self):
        sale_order_ids = self.env['wiz_sale_order_print_etiq'].browse(self._ids)
        res = sale_order_ids.load_order_line('order')
        
        if len(res) >= 1:
            action = self.env.ref('hubi.action_wiz_sale_order_print_etiq_tree').read()[0]
            action['domain'] = [('id', 'in', res)]
         
            return action  


    @api.depends('company_id')
    def _calcul_lot(self):
        val_calcul_lot = 'M'
        #settings = self.env['hubi.general_settings'].search([('name','=', 'General Settings'), ('company_id','=', self.company_id.id)])
        #for settings_vals in settings:
        #    if settings_vals.calcul_lot:
        #        val_calcul_lot = settings_vals.calcul_lot
        val_calcul_lot = self.env['ir.config_parameter'].sudo().get_param("di_calcul_lot")
        self.di_calcul_lot = val_calcul_lot
        

    #shipper_id = fields.Many2one('hubi.shipper', string='Shipper')
    di_comment = fields.Text(string='Comment')
    #order_reference = fields.Char(string='Order Reference')
    di_sending_date = fields.Date(string="Sending Date", default=lambda self: fields.Date.today())   
    di_packaging_date = fields.Date(string="Packaging Date", default=lambda self: fields.Date.today())   
    di_calcul_lot = fields.Text(string="Batch Number Calculation", store=False, compute='_calcul_lot')
    
    di_pallet_number = fields.Integer(string = 'Number of pallet')
    
    #di_periodicity_invoice = fields.Selection(string="Invoice Period", related='partner_id.di_periodicity_invoice')#,store=True)
    #di_invoice_grouping = fields.Boolean(string="Invoice grouping", related='partner_id.di_invoice_grouping')#,store=True)
    #di_carrier_id = fields.Integer(string="Delivery Method", related='partner_id.carrier_id')#,store=True)


#    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id_shipper(self):
        """
        Update the following fields when the partner is changed:
        - Carrier
        """
        if not self.partner_id:
            self.update({
                'carrier_id': False,

            })
            return
    
        values = { 
            'carrier_id' : self.partner_id.property_delivery_carrier_id and self.partner_id.property_delivery_carrier_id.id or False
            }

        #if self.partner_id.shipper_id:
        #    values['shipper_id'] = self.partner_id.shipper_id and self.partner_id.shipper_id.id or False
        self.update(values)
        

    def action_invoice_create_new(self, grouped=False, final=False, dateInvoice=False):
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
        
        account_divers  = self.env['product.category'].search([('di_reference', 'in', ['D', 'd', 'DIVERS','Divers','divers',''] )], limit=1 ) 
        if not dateInvoice:
            date_invoices = time.strftime('%Y-%m-%d')
        else:
            date_invoices = dateInvoice 
               
        date_due = False

        # 1) Create invoices.
        invoice_vals_list = []
        invoice_item_sequence = 0
        for order in self.sorted(key=lambda r: (r.partner_invoice_id.id, r.id)):
            order = order.with_company(order.company_id)
            current_section_vals = None
            down_payments = order.env['sale.order.line']

            inv_group = grouped
            if order.partner_invoice_id.di_invoice_grouping:
               inv_group = False
            else:
               inv_group = True
                   
            group_key = order.id if inv_group else (order.partner_invoice_id.id, order.currency_id.id)

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
                    dateorder=fields.Date.from_string(order.date_order).strftime('%d/%m/%Y')
                    res = {
                        'display_type': False, #'line_note',
                        'sequence':invoice_item_sequence + 1,
                        'name': 'BL no ' + order.name + ' du ' + dateorder,
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


#    @api.multi
    def _prepare_invoice(self,):
        invoice_vals = super(HubiSaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'di_discount_type': 'percent',
            'di_discount_rate': self.partner_invoice_id.di_discount_invoice
        })
        return invoice_vals     
     
#    @api.multi
    #def print_quotation(self):
    #    self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
    #    return self.env.ref('hubi.action_report_saleorder_hubi').report_action(self)
    """
    def preview_sale_order(self):
        self.ensure_one()
        
        #source = 'fsm' if self.env.context.get('fsm_mode', False) else 'project'
        #'url': self.get_portal_url(suffix='/worksheet/%s' % source)
        #suffix='hubi.action_report_saleorder_hubi' )
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url() ,

        }
    """    

    def sale_order_send_email(self):
        #raise UserError(_('Send email.'))
        attachments_ids = []
        Envoi = False
        NbLig = len(self.ids)
        CodePartner=999999
        EMailPartner="z"
        CptLig = 0
        for ligne in self.sorted(key=lambda r: (r.partner_id.email, r.id)):
            CptLig = CptLig + 1
           
            if ((ligne.partner_id.email != EMailPartner) and (EMailPartner != "z")) :
                self.send_email(ligne,EMailPartner,attachments_ids)
                Envoi = False
                attachments_ids = []
                
            if ligne.partner_id.email:
                CodePartner = ligne.partner_id.id
                EMailPartner = ligne.partner_id.email
                Envoi = True
 
                #pdf = self.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf([ligne.id])[0]
                pdf = self.env.ref('hubi.action_report_saleorder_hubi').sudo()._render_qweb_pdf([ligne.id])[0]
                # attachment
            
                id_w = self.env['ir.attachment'].create({
                    'name': 'Sale order'+(ligne.display_name)+"_"+str(ligne.id),
                    'type': 'binary', 
                    'res_id':ligne.id,
                    'res_model':'sale.order',
                    'datas':base64.b64encode(pdf),
                    'mimetype': 'application/x-pdf',
                    'store_fname':ligne.display_name+'_'+str(ligne.id)+'.pdf'
                    })
                attachments_ids.append(id_w.id)
            
        if (Envoi):
            self.send_email(ligne,EMailPartner,attachments_ids)  
            #raise UserError(_('Email send.')) 
        
         #return True
    
    def send_email(self,ligne,email_to,attachments_ids):    
        
        #if not ligne.partner_id.email:
        #    raise UserError(_("Cannot send email: partner %s has no email address.") % ligne.partner_id.name)
        if email_to:
            current_uid = self._context.get('uid')
            su_id_current = self.env['res.partner'].browse(current_uid)
            
            su_id = self.env['res.partner'].browse(SUPERUSER_ID)
            template_id = self.env['ir.model.data'].get_object_reference('hubi',  'email_template_sale_order')[1]
            template_browse = self.env['mail.template'].browse(template_id)
            #email_to = self.env['res.partner'].browse(ligne.partner_id).email
            
            if template_browse:
                #values = template_browse.generate_email(ligne.id, fields=None)
                values = template_browse.generate_email(ligne.id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
                values['email_to'] = email_to
                values['email_from'] = su_id_current.email 
                #values['email_from'] = su_id.email
                values['res_id'] = ligne.id   #False
                if not values['email_to'] and not values['email_from']:
                    pass
                
                values['attachment_ids'] = [(6, 0, attachments_ids)] #attachments_ids
                                
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.create(values)
                if msg_id:
                    mail_mail_obj.send(msg_id) 
    
    def action_confirm(self):
        res = super(HubiSaleOrder, self).action_confirm()
        self.update_sale_batch_number()
        return res
        
        
        
#    @api.multi
    def update_sale_batch_number(self):
        date_calcul = False
        val_calcul_lot_date = self.env['ir.config_parameter'].sudo().get_param('hubi.di_calcul_lot_date')
        if val_calcul_lot_date == 'Sale':
           if self.date_order:
              date_calcul = self.date_order 
              
        if val_calcul_lot_date == 'Send':
           if self.di_sending_date:
              date_calcul = self.di_sending_date 
        if val_calcul_lot_date == 'Packaging':
           if self.di_packaging_date:
              date_calcul = self.di_packaging_date 

            
        if date_calcul:
            _nolot =''
            self.env.cr.commit()
            val_calcul_lot = 'M'
            
            #('M', 'Manual'), ('AAAAMMJJ', 'Auto AAAAMMJJ'), ('AAMMJJ', 'Auto AAMMJJ'), ('AAAAQ', 'Auto AAAAQQQ'), ('AAQ', 'Auto AAQQQ'), ('JJ/MM/AAAA', 'Auto JJ/MM/AAAA'), ('JJ/MM/AA', 'Auto JJ/MM/AA')
            #settings = self.env['hubi.general_settings'].search([('name','=', 'General Settings'), ('company_id','=', self.company_id.id)])
            #for settings_vals in settings:
            #    if settings_vals.di_calcul_lot:
            #        val_calcul_lot = settings_vals.di_calcul_lot

            val_calcul_lot = self.env['ir.config_parameter'].sudo().get_param('hubi.di_calcul_lot')
            
            dateAAAAMMJJ=fields.Date.from_string(date_calcul).strftime('%Y%m%d')
            dateAAMMJJ=fields.Date.from_string(date_calcul).strftime('%y%m%d')
            dateAAAAQQQ=fields.Date.from_string(date_calcul).strftime('%Y%j')
            dateAAQQQ=fields.Date.from_string(date_calcul).strftime('%y%j')
            dateJJ_MM_AAAA=fields.Date.from_string(date_calcul).strftime('%d/%m/%Y')
            dateJJ_MM_AA=fields.Date.from_string(date_calcul).strftime('%d/%m/%y')
            
            if val_calcul_lot=='AAAAQ': 
                _nolot = dateAAAAQQQ
            if val_calcul_lot=='AAQ': 
                _nolot = dateAAQQQ
            if val_calcul_lot=='AAAAMMJJ': 
                _nolot = dateAAAAMMJJ
            if val_calcul_lot=='AAMMJJ': 
                _nolot = dateAAMMJJ
            if val_calcul_lot=='JJ/MM/AAAA': 
                _nolot = dateJJ_MM_AAAA
            if val_calcul_lot=='JJ/MM/AA': 
                _nolot = dateJJ_MM_AA
            
            if _nolot !='':
                order_lines = self.env['sale.order.line'].search([('order_id', '=', self.id)])
                for line in order_lines:
                    line.write({'di_no_lot':_nolot})
        
        return {'type': 'ir.actions.act_window_close'}
    
 
    #@api.onchange('di_sending_date')
    #def onchange_sending_date(self):
    #    if self.di_calcul_lot != 'M':
    #        self.update_sale_batch_number()
 
    """
    #    @api.multi
    def action2_palletization2(self):
        action = self.env.ref('hubi.action_hubi_palletization').read()[0]
        action['views'] = [(self.env.ref('hubi.hubi_palletization_form').id, 'form')]
        action['res_id'] = self.id

        return action
        #return {'type': 'ir.actions.act_window_close'} 
       
    def create_pallet_sale(self):        
        res = super(HubiSaleOrder, self).create_pallet_sale()
        company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id
        id_order = self.id
        
        palletization_ids = self.env['di.palletization'].search([('order_id', '=', id_order),  ('company_id', '=', company_code)])
        for pallets in palletization_ids:
            lines = self.env['sale.order.line'].search([('order_id', '=', id_order), ('product_id', '=', pallets.product_id.id),  ('company_id', '=', company_code)])
            for line in lines:
                batch_number = lines.di_no_lot
                date_limit = lines.di_date_dluo
                
            pallets.update({
                            'batch_number': batch_number,
                            'date_limit': date_limit,
                    
                        })
   
   
    def create_print_etiquet_pallet(self, id_order= False):        
        id_order = self.id
        res = super(HubiSaleOrder, self).create_print_etiquet_pallet(id_order)
        company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id
        
        etab_exp_no = self.partner_id.di_sender_establishment.id
        sending_date = ""
        packaging_date = ""
        if self.di_sending_date:
           sending_date = fields.Date.from_string(self.di_sending_date).strftime('%d/%m/%Y')
        if self.di_packaging_date:    
           packaging_date = fields.Date.from_string(self.di_packaging_date).strftime('%d/%m/%Y')
                
        palletization_ids = self.env['wiz.print.pallet'].search([('sale_order_id', '=', id_order),  ('company_id', '=', company_code)])
        for pallets in palletization_ids:
            
                
            pallets.update({
                'etab_exped_id' : etab_exp_no,
                'sending_date' : sending_date,
                'packaging_date' : packaging_date,          
                        })

    """