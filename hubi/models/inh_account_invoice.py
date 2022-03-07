# -*- coding: utf-8 -*-
from functools import partial
from odoo import models, fields, api, tools, _, SUPERUSER_ID
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError, AccessError
import base64


class HubiAccountInvoice(models.Model):
    _inherit = "account.move"

 
    #invoice_date = fields.Date(string='Invoice Date',
    #                           readonly=True, states={'draft': [('readonly', False)]}, index=True,
    #                           help="Keep empty to use the current date", copy=False,
    #                           default=lambda self: fields.Date.today())
    di_pallet_number = fields.Integer(string='Number of pallet')
    di_comment = fields.Text(string='Comment')
    di_sending_date = fields.Date(string="Sending Date")
    di_packaging_date = fields.Date(string="Packaging Date")
    di_carrier_id = fields.Many2one('delivery.carrier', string='Carrier')

    di_discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='percent')
    di_discount_rate = fields.Float('Discount Amount', digits=(16, 2), readonly=True,
                                 states={'draft': [('readonly', False)]})
    di_amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_compute_amount',
                                     tracking=True) # track_visibility='always')

    #di_amount_before_discount = fields.Monetary(string='Amount before discount',
    #           store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    #di_amount_before_discount_signed = fields.Monetary(string='Amount before discount in Company Currency',
    #            currency_field='company_currency_id', store=True, readonly=True, compute='_compute_amount')
    #di_amount_discount_signed = fields.Monetary(string='Amount discount in Company Currency',
    #            currency_field='company_currency_id', store=True, readonly=True, compute='_compute_amount')
    #di_amount_tax_signed = fields.Monetary(string='Tax Amount in Company Currency', currency_field='company_currency_id',
    #                                   store=True, readonly=True, compute='_compute_amount')

    #    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id_shipper(self):
        """
        Update the following fields when the partner is changed:
        - Carrier
        """
        if not self.partner_id:
            self.update({
                'di_carrier_id': False,

            })
            return

        values = {
            'di_carrier_id': self.partner_id.property_delivery_carrier_id and self.partner_id.property_delivery_carrier_id.id or False
        }

        self.update(values)

    #@api.onchange('di_discount_type', 'di_discount_rate', 'invoice_line_ids')
    #def supply_rate(self):
        """
        for inv in self:
            if inv.di_discount_type == 'percent':
                for line in inv.invoice_line_ids:
                    line.discount = inv.di_discount_rate
            else:
                total = discount = 0.0
                for line in inv.invoice_line_ids:
                    total += (line.quantity * line.price_unit)
                if inv.di_discount_rate != 0:
                    discount = (inv.di_discount_rate / total) * 100
                else:
                    discount = inv.di_discount_rate
                for line in inv.invoice_line_ids:
                    line.discount = discount
        """

    """
    #    @api.multi
    def compute_invoice_totals(self, company_currency, invoice_move_lines):
        total = 0
        total_currency = 0
        for line in invoice_move_lines:
            if self.currency_id != company_currency:
                currency = self.currency_id.with_context(
                    date=self.date or self.invoice_date or fields.Date.context_today(self))
                line['currency_id'] = currency.id
                line['amount_currency'] = currency.round(line['price'])
                line['price'] = currency.compute(line['price_subtotal'], company_currency)
            else:
                line['currency_id'] = False
                line['amount_currency'] = False
                line['price'] = line['price']
                
            if self.move_type in ('out_invoice', 'in_refund'):
                total += line['price']
                total_currency += line['amount_currency'] or line['price']
                line['price'] = - line['price']
            else:
                total -= line['price']
                total_currency -= line['amount_currency'] or line['price']
                
        return total, total_currency, invoice_move_lines
    """

    #    @api.multi
    #def button_dummy(self):
    #    self.supply_rate()
    #    return True

#    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        
        return self.env.ref('hubi.account_invoices_hubi').report_action(self)
        
    #    @api.multi
    def invoice_send_email(self):
        #raise UserError(_('Send email.'))
        attachments_ids = []
        Envoi = False
        NbLig = len(self.ids)
        CodePartner = 999999
        EMailPartner = "z"
        CptLig = 0
        # for ligne in self.sorted(key=lambda r: (r.partner_id.id, r.id)):
        for ligne in self.sorted(key=lambda r: (r.partner_id.email, r.id)):
            CptLig = CptLig + 1

            # if ((ligne.partner_id.id != CodePartner) and (CodePartner != 999999)) or (CptLig == NbLig):
            if ((ligne.partner_id.email != EMailPartner) and (EMailPartner != "z")):
                self.send_email(ligne, EMailPartner, attachments_ids)
                Envoi = False
                attachments_ids = []

            if ligne.partner_id.email:
                CodePartner = ligne.partner_id.id
                EMailPartner = ligne.partner_id.email
                Envoi = True

                pdf = self.env.ref('account.account_invoices').sudo()._render_qweb_pdf([ligne.id])[0]
                #pdf = self.env.ref('hubi.account_invoices_hubi').sudo()._render_qweb_pdf([ligne.id])[0]

                id_w = self.env['ir.attachment'].create({
                    'name': 'Invoice_' + (ligne.display_name) + "_" + str(ligne.id) + '.pdf',
                    'type': 'binary',
                    'res_id': ligne.id,
                    'res_model': 'account.move',
                    'datas': base64.b64encode(pdf),
                    'mimetype': 'application/x-pdf',
                    'store_fname': ligne.display_name + '_' + str(ligne.id) + '.pdf'
                })
                attachments_ids.append(id_w.id)

        if (Envoi):
            self.send_email(ligne, EMailPartner, attachments_ids)


    def send_email(self, ligne, email_to, attachments_ids):

        # if not ligne.partner_id.email:
        #    raise UserError(_("Cannot send email: partner %s has no email address.") % ligne.partner_id.name)
        if email_to:
            current_uid = self._context.get('uid')
            su_id_current = self.env['res.partner'].browse(current_uid)
            
            su_id = self.env['res.partner'].browse(SUPERUSER_ID)
            template_id = self.env['ir.model.data'].check_object_reference('hubi', 'email_template_invoice', True)[1]
            template_browse = self.env['mail.template'].browse(template_id)
            # email_to = self.env['res.partner'].browse(ligne.partner_id).email

            if template_browse:
                #values = template_browse.generate_email(ligne.id, fields=None)
                values = template_browse.generate_email(ligne.id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
                values['email_to'] = email_to
                values['email_from'] = su_id.email
                values['res_id'] = ligne.id  # False
                if not values['email_to'] and not values['email_from']:
                    pass

                values['attachment_ids'] = [(6, 0, attachments_ids)]  

                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.create(values)
                if msg_id:
                    mail_mail_obj.send(msg_id)

    @api.model
    def _move_autocomplete_invoice_lines_create(self, vals_list):
            
        #copie standard
        ''' During the create of an account.move with only 'invoice_line_ids' set and not 'line_ids', this method is called
        to auto compute accounting lines of the invoice. In that case, accounts will be retrieved and taxes, cash rounding
        and payment terms will be computed. At the end, the values will contains all accounting lines in 'line_ids'
        and the moves should be balanced.

        :param vals_list:   The list of values passed to the 'create' method.
        :return:            Modified list of values.
        '''
        new_vals_list = []
        for vals in vals_list:
            if not vals.get('invoice_line_ids'):
                new_vals_list.append(vals)
                continue
            # modif pour toujours mettre à jour avec les données saisies
#            if vals.get('line_ids'):
#                vals.pop('invoice_line_ids', None)
#                new_vals_list.append(vals)
#                continue
            #fin modif
            if not vals.get('move_type') and not self._context.get('default_move_type'):
                vals.pop('invoice_line_ids', None)
                new_vals_list.append(vals)
                continue
            vals['move_type'] = vals.get('move_type', self._context.get('default_move_type', 'entry'))
            if not vals['move_type'] in self.get_invoice_types(include_receipts=True):
                new_vals_list.append(vals)
                continue

            vals['line_ids'] = vals.pop('invoice_line_ids')

            if vals.get('invoice_date') and not vals.get('date'):
                vals['date'] = vals['invoice_date']

            ctx_vals = {'default_move_type': vals.get('move_type') or self._context.get('default_move_type')}
            if vals.get('currency_id'):
                ctx_vals['default_currency_id'] = vals['currency_id']
            if vals.get('journal_id'):
                ctx_vals['default_journal_id'] = vals['journal_id']
                # reorder the companies in the context so that the company of the journal
                # (which will be the company of the move) is the main one, ensuring all
                # property fields are read with the correct company
                journal_company = self.env['account.journal'].browse(vals['journal_id']).company_id
                allowed_companies = self._context.get('allowed_company_ids', journal_company.ids)
                reordered_companies = sorted(allowed_companies, key=lambda cid: cid != journal_company.id)
                ctx_vals['allowed_company_ids'] = reordered_companies
            self_ctx = self.with_context(**ctx_vals)
            new_vals = self_ctx._add_missing_default_values(vals)

            move = self_ctx.new(new_vals)
            new_vals_list.append(move._move_autocomplete_invoice_lines_values())

        return new_vals_list

    def _move_autocomplete_invoice_lines_write(self, vals):
        #copie standard
        ''' During the write of an account.move with only 'invoice_line_ids' set and not 'line_ids', this method is called
        to auto compute accounting lines of the invoice. In that case, accounts will be retrieved and taxes, cash rounding
        and payment terms will be computed. At the end, the values will contains all accounting lines in 'line_ids'
        and the moves should be balanced.

        :param vals_list:   A python dict representing the values to write.
        :return:            True if the auto-completion did something, False otherwise.
        '''
        
        # modif pour toujours mettre à jour avec les données saisies
        if not vals.get('invoice_line_ids'):
            return False
#        enable_autocomplete = 'invoice_line_ids' in vals and 'line_ids' not in vals and True or False

#        if not enable_autocomplete:
#            return False
        #fin modif
        
        vals['line_ids'] = vals.pop('invoice_line_ids')
        for invoice in self:
            invoice_new = invoice.with_context(default_move_type=invoice.move_type, default_journal_id=invoice.journal_id.id).new(origin=invoice)
            invoice_new.update(vals)
            values = invoice_new._move_autocomplete_invoice_lines_values()
            values.pop('invoice_line_ids', None)
            invoice.write(values)
        return True




class HubiAccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('di_category_id', 'di_caliber_id', 'di_packaging_id')
    def _onchange_product(self):
        global id_prod_prod
        if self.move_id.move_type in ['in_invoice', 'in_refund']:
            product_domain = [('purchase_ok', '=', True)]
        else:    
            product_domain = [('sale_ok', '=', True)]

        if self.di_category_id:
            product_domain = [('categ_id', '=', self.di_category_id.id)] + product_domain[0:]
        if self.di_caliber_id:
            product_domain = [('di_caliber_id', '=', self.di_caliber_id.id)] + product_domain[0:]
        if self.di_packaging_id:
            product_domain = [('di_packaging_id', '=', self.di_packaging_id.id)] + product_domain[0:]

        if self.di_category_id and self.di_caliber_id and self.di_packaging_id:
            # Recherche de l'artcle en fonction des sélections 
            id_prod = 0
            products_templ = self.env['product.template'].search([
                ('categ_id', '=', self.di_category_id.id),
                ('di_caliber_id', '=', self.di_caliber_id.id),
                ('di_packaging_id', '=', self.di_packaging_id.id), ])
            for prod in products_templ:
                id_prod = prod.id

            if id_prod != 0:
                # search the code in product.product
                products_prod_prod = self.env['product.product'].search([
                    ('product_tmpl_id', '=', id_prod), ])
                for prod_prod in products_prod_prod:
                    id_prod_prod = prod_prod.id

                self.product_id = id_prod_prod

        return {'domain': {'product_id': product_domain}}

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

    #    @api.one
    @api.depends('price_total', 'price_subtotal')
    def compute_price(self):
        #self.ensure_one()
        sign = 1
        
        for line in self:
            currency = line.move_id and line.move_id.currency_id or None
            price_total_signed: float = 0.0
            price_subtotal_signed: float = 0.0
            price_total_signed = line.price_total
            price_subtotal_signed = line.price_subtotal
        
            if line.move_id.currency_id and line.move_id.currency_id != line.move_id.company_id.currency_id:
                price_total_signed = line.move_id.currency_id.with_context(
                    date=line.move_id._get_currency_rate_date()).compute(price_total_signed,
                                                                        line.move_id.company_id.currency_id)
                price_subtotal_signed = line.move_id.currency_id.with_context(
                    date=line.move_id._get_currency_rate_date()).compute(price_subtotal_signed,
                                                                        line.move_id.company_id.currency_id)

            sign = line.move_id.move_type in ['in_invoice', 'out_refund','in_receipt'] and -1 or 1        # ['in_refund', 'out_refund']
            line.di_price_total_signed = price_total_signed * sign
            line.di_price_subtotal_signed = price_subtotal_signed * sign
        
            #line.update(line._get_price_total_and_subtotal())
            #line.update(line._get_fields_onchange_subtotal())
        
        
    #    @api.one
    @api.depends('quantity', 'price_total', 'product_id')
    def _compute_weight(self):
        """
        Compute the weights of the account invoice lines.
        """
        #self.ensure_one()
        
        #sign = 1
        #if self.move_id.move_type in ('in_invoice', 'out_refund','in_receipt'):       #('in_refund', 'out_refund')
        #    sign = -1

        for line in self:
            weight: float = 0.0
            weight_signed: float = 0.0
            sign = 1
            if line.move_id.move_type in ('in_invoice', 'out_refund','in_receipt'):      
                sign = -1
            
            factor = line.product_uom_id.factor * line.product_id.uom_id.factor
            if factor != 0:
                weight = line.product_id.weight * (line.quantity / factor)
            else:
                weight = line.product_id.weight * line.quantity
            weight = round(weight, 3)

            weight_signed = weight * sign

            if weight != 0:
                if line.discount >=100:
                    price_weight = (line.price_unit * line.quantity) / weight
                else:
                    price_weight = line.price_subtotal / weight
            else:
                price_weight = 0

            price_weight = round(price_weight, 3)

            line.di_weight = weight
            line.di_weight_signed = weight_signed
            line.di_price_weight= price_weight
           
            #line.update({
            #    'di_weight': weight,
            #    'di_weight_signed': weight_signed,
            #    'di_price_weight': price_weight
            #})
        




    di_category_id = fields.Many2one('product.category', 'Internal Category',
                                  domain=[('parent_id', '!=', False), ('di_shell', '=', True)], store=False)
    di_caliber_id = fields.Many2one('di.multi.table', string='Caliber', domain=[('record_type', '=', 'Caliber')],
                                 help="The Caliber of the product.", store=False)
    di_packaging_id = fields.Many2one('di.multi.table', string='Packaging', domain=[('record_type', '=', 'Packaging')],
                                   help="The Packaging of the product.", store=False)
    di_weight = fields.Float(string='Weight ', store=True, readonly=True, compute='_compute_weight')
    di_price_weight = fields.Float(string='Price Weight ', store=True, readonly=True, compute='_compute_weight')
    di_weight_signed = fields.Float(string='Weight Signed', store=True, readonly=True, compute='_compute_weight')
    di_price_subtotal_signed = fields.Monetary(string='Amount subtotal Signed in Company Currency',
                                         currency_field='company_currency_id',
                                         store=True, readonly=True, compute='compute_price')
    di_price_total_signed = fields.Monetary(string='Amount total Signed in Company Currency',
                                         currency_field='company_currency_id',
                                         store=True, readonly=True, compute='compute_price')
    #di_comment = fields.Char(string='Comment')
    di_commentary = fields.Char(string='Commentary')



# class AccountInvoiceTax(models.Model):
#    _inherit = "account.invoice.tax"

# @api.depends('invoice_id.discount_type', 'invoice_id.discount_rate', 'invoice_id.invoice_line_ids')
# def compute_rate_discount(self):
#    rate_d = 0
#    for invoice in self.mapped('move_id'):
#        if invoice.discount_type == 'percent':
#            rate_d = invoice.discount_rate
#        else:
#            total = discount = 0.0
#            for line in invoice.tax_line_ids:
#                total += (line.base)
#            if invoice.discount_rate != 0:
#                rate_d = (invoice.discount_rate / total) * 100


#    for tax in self:
#        tax.base_discount = 0.0
#        tax.amount_discount = 0.0
#        if tax.tax_id:
#           tax.base_discount = tax.base * rate_d/100
#           tax.amount_discount = tax.base_discount  * tax.tax_id.amount /100


# amount_discount = fields.Monetary(string="Amount Discount", compute='compute_rate_discount', store=True)
# base_discount = fields.Monetary(string="Base Discount", compute='compute_rate_discount', store=True)


# @api.depends('amount', 'amount_rounding')
# def _compute_amount_total(self):
#    for tax_line in self:
#        tax_line.amount_total = tax_line.amount + tax_line.amount_rounding - tax_line.amount_discount
