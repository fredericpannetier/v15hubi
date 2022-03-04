# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import time
import calendar
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class Wizard_create_invoice_period(models.TransientModel):
    _name = "wiz.invoiceperiod"
    _description = "Wizard creation of invoice from period"

#     def add_months(sourcedate, months):
#         month = sourcedate.month - 1 + months
#         year = sourcedate.year + month // 12
#         month = month % 12 + 1
#         day = min(sourcedate.day, calendar.monthrange(year, month)[1])
#         return datetime.date(year, month, day)

    #    @api.model
    def _default_start(self):
        return fields.Date.context_today(self)

    #    @api.model
    def _default_finish(self):
        finish = datetime.today() + timedelta(days=7)
        return fields.Date.context_today(self, timestamp=finish)

    #    @api.model
    @api.onchange('periodicity_invoice')
    def onchange_periodicity_invoice(self):
        finish = datetime.today()

        if self.periodicity_invoice == "Weekly":
            finish = datetime.today() + timedelta(days=-7)
        if self.periodicity_invoice == "Decade":
            finish = datetime.today() + timedelta(days=-10)
        if self.periodicity_invoice == "Fortnight":
            finish = datetime.today() + timedelta(days=-14)
        if self.periodicity_invoice == "Monthly":
            # start_date = datetime.today()
            # days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
            # finish = start_date + timedelta(days=-days_in_month)
            finish = datetime.today() + relativedelta(months=-1)

        self.date_start = finish

    periodicity_invoice = fields.Selection([("Daily", "Daily"), ("Weekly", "Weekly"), ("Decade", "Decade"),
                                            ("Fortnight", "Fortnight"), ("Monthly", "Monthly")],
                                           string="Invoice Period", default='Daily')
    # date_start = fields.Date('Start Date', help="Starting date for the creation of invoices",default=_default_finish)
    date_start = fields.Date('Start Date', help="Starting date for the creation of invoices",
                             default=lambda self: fields.Date.today())
    date_end = fields.Date('End Date', help="Ending valid for the the creation of invoices",
                           default=lambda self: fields.Date.today())
    ref_start = fields.Char(required=True, default=" ", string="Start Customer Reference")
    ref_end = fields.Char(required=True, default="zzzzzzzzzz", string="End Customer Reference")

    invoice_date = fields.Date(string="Invoice Date", default=lambda self: fields.Date.today())
    direct_creat = fields.Boolean("Creat invoice immediatly",default=False)
    
    sale_order_ids = fields.Many2many("sale.order")
    message = fields.Text(string="Information")

#   @api.multi
    def di_create_invoices(self, ids, regr, date_fact, period_fact, date_start, date_end, ref_start, ref_end):
        sale_orders = self.env['sale.order'].browse(ids)
        if sale_orders:
            self._cr.execute('SAVEPOINT create_invoices')
            try:
                sale_orders.action_invoice_create(grouped=not regr, final=True, dateInvoice=date_fact)
                self._cr.commit()  
                for s_o in sale_orders: #pour passer en complètement facturé les commandes avec reliquat
                    self._cr.execute('SAVEPOINT done_sale')
                    try:
                        s_o.action_done() 
                        self._cr.commit()  
                    except Exception as e:
                        self._cr.execute('ROLLBACK TO SAVEPOINT done_sale') 
                        self.env['ir.logging'].sudo().create({
                                'name': 'creat_invoice',
                                'type': 'server',
                                'level': 'ERROR',
                                'dbname': self.env.cr.dbname,
                                'message': 'Error in done for sale order',
                                'func': 'di_create_invoices',
                                'path': '',
                                'line': '0',
                            })  
            except Exception as e:
                self._cr.execute('ROLLBACK TO SAVEPOINT create_invoices') 
                self.env['ir.logging'].sudo().create({
                        'name': 'creat_invoice',
                        'type': 'server',
                        'level': 'ERROR',
                        'dbname': self.env.cr.dbname,
                        'message': 'Error in creat invoices',
                        'func': 'di_create_invoices',
                        'path': '',
                        'line': '0',
                    })   
                             
                                    
        invoices = sale_orders.mapped('invoice_ids')
        draft_invoices = invoices.filtered(lambda f: f.state == 'draft')
        #draft_invoices.write({'date_invoice':date_fact})

        for draft_invoice in draft_invoices:
                self._cr.execute('SAVEPOINT validate_invoice')
                try:
                    draft_invoice.action_invoice_open()                    
                    self._cr.commit()
                except Exception as e:
                    self._cr.execute('ROLLBACK TO SAVEPOINT validate_invoice')
                    # log error in ir.logging for a visibility on the error
                    self.env['ir.logging'].sudo().create({
                        'name': 'Validation_facture',
                        'type': 'server',
                        'level': 'ERROR',
                        'dbname': self.env.cr.dbname,
                        'message': 'Erreur validation facture',
                        'func': 'di_create_invoices',
                        'path': '',
                        'line': '0',
                    })
                    
                    
        mail_fin = self.env['mail.mail'].create({"subject":"Facturation terminée","email_to":self.env.user.email,"body_html":"La facturation est terminée.","body":"La facturation est terminée."})
        mail_fin.send() 
        
                    

    #    @api.multi
    def create_invoice_period(self):
        #date_fin = datetime.str(self.date_end, "%Y-%m-%d") + timedelta(hours=25) + timedelta(
        #    minutes=59) + timedelta(seconds=59)
        
        fini = False           
        self.env.cr.execute("""SELECT id FROM ir_model 
                                  WHERE model = %s""", (str(self._name),))            
        info = self.env.cr.dictfetchall()  
        if info:
            model_id = info[0]['id']   
        
        date_deb = self.date_start.strftime('%Y%m%d')
        date_fin = datetime.strptime(self.date_end, "%Y-%m-%d")  + timedelta(hours=25) + timedelta(minutes=59) + timedelta(seconds=59)
        #date_fin = self.date_end.strftime('%Y%m%d')
        query_args = {'periodicity_invoice': self.periodicity_invoice, 'date_start': date_deb,
                      'date_end': date_fin}
        query = """ SELECT  sale_order.id 
                        FROM sale_order 
                        INNER JOIN res_partner on res_partner.id = sale_order.partner_invoice_id 
                        WHERE invoice_status = 'to invoice' 
                        AND date_order between %(date_start)s AND %(date_end)s
                        AND di_periodicity_invoice=%(periodicity_invoice)s 
                        ORDER BY res_partner.id """

        self.env.cr.execute(query, query_args)
        ids = [r[0] for r in self.env.cr.fetchall()]
        sale_orders = self.env['sale.order'].search([('id', 'in', ids)])

        sale_orders.action_invoice_create(dateInvoice=self.invoice_date)
        #self.invoice_create(sale_orders)
        # return {'type': 'ir.actions.act_window_close'}
        return sale_orders.action_view_invoice()


    def invoice_create(self, sale_orders):
        sale_orders.action_invoice_create(dateInvoice=self.invoice_date)
        """
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

                if order.di_comment and not invoice.di_comment:
                    invoice.write({'di_comment': order.di_comment})

                if order.carrier_id.id and not invoice.di_carrier_id:
                    invoice.write({'di_carrier_id': order.carrier_id.id})
        """
        
   #    @api.multi
    def create_invoice_period_cron(self):
        #finish = datetime.today() + timedelta(days=7)
        fini = False           
        self.env.cr.execute("""SELECT id FROM ir_model 
                                  WHERE model = %s""", (str(self._name),))            
        info = self.env.cr.dictfetchall()  
        if info:
            model_id = info[0]['id']   
        
        date_deb = self.date_start.strftime('%Y%m%d')
        
        #date_fin = datetime.strptime(self.date_end, "%Y-%m-%d")  + timedelta(hours=25) + timedelta(minutes=59) + timedelta(seconds=59)
        date_fin = self.date_end + timedelta(hours=24)
        
        date_fin = date_fin.strftime('%Y%m%d')
        #date_fin = self.date_end.strftime('%Y%m%d')
        query_args = {'periodicity_invoice': self.periodicity_invoice, 'date_start': date_deb, 'date_end': date_fin, 'ref_start': self.ref_start, 'ref_end': self.ref_end}
        query = """ SELECT  sale_order.id 
                        FROM sale_order 
                        INNER JOIN res_partner on res_partner.id = sale_order.partner_invoice_id 
                        WHERE invoice_status = 'to invoice' 
                        AND date_order between %(date_start)s AND %(date_end)s
                        AND di_periodicity_invoice=%(periodicity_invoice)s 
                        AND (res_partner.ref is null OR res_partner.ref between %(ref_start)s AND %(ref_end)s)
                        ORDER BY res_partner.id """

        self.env.cr.execute(query, query_args)
        ids = [r[0] for r in self.env.cr.fetchall()]
        sale_orders = self.env['sale.order'].search([('id', 'in', ids)])

        if self.direct_creat:
            sale_orders.action_invoice_create(dateInvoice=self.invoice_date)
        
        else:
            # par cron
            if sale_orders:
                partners = sale_orders.mapped('partner_id')
                cptpart = 0
                to_invoice = self.env['sale.order']
                dateheureexec =False
                for partner in partners:      
                    cptpart +=1                  
                    partner_orders = sale_orders.filtered(lambda so: so.partner_id.id == partner.id)
                    dateheure = datetime.today()                              
                    to_invoice+=partner_orders
                    if cptpart == 30:
                        cptpart =0
                        if not dateheureexec:
                            dateheureexec = dateheure + timedelta(minutes=1)
                        else:
                            dateheureexec = dateheureexec + timedelta(minutes=15)
                        
                        self.env['ir.cron'].create({'name':'Fact. ' + dateheure.strftime("%m/%d/%Y %H:%M:%S"), 
                                                'active':True, 
                                                'user_id':self.env.user.id, 
                                                'interval_number':1, 
                                                'interval_type':'days', 
                                                'numbercall':1, 
                                                'doall':1, 
                                                'nextcall':dateheureexec, 
                                                'model_id': model_id, 
                                                'code': 'model.di_create_invoices(('+str(to_invoice.ids).strip('[]')+'),%s, "%s","%s","%s","%s","%s","%s")' % (True , self.invoice_date, self.periodicity_invoice, self.date_start, self.date_end, self.ref_start, self.ref_end),
                                                'state':'code',
                                                'priority':0})    
                        to_invoice = self.env['sale.order']  
                        fini=True  
                        break       
                    
                if cptpart > 0 and not fini:
                    if not dateheureexec:
                        dateheureexec = dateheure + timedelta(minutes=1)
                    else:
                        dateheureexec = dateheureexec + timedelta(minutes=15)
                    
                    self.env['ir.cron'].create({'name':'Fact. ' + dateheure.strftime("%m/%d/%Y %H:%M:%S"), 
                                            'active':True, 
                                            'user_id':self.env.user.id, 
                                            'interval_number':1, 
                                            'interval_type':'days', 
                                            'numbercall':1, 
                                            'doall':1, 
                                            'nextcall':dateheureexec, 
                                            'model_id': model_id, 
                                            'code': 'model.di_create_invoices(('+str(to_invoice.ids).strip('[]')+'),%s, "%s","%s","%s","%s","%s","%s")' % (True , self.invoice_date, self.periodicity_invoice, self.date_start, self.date_end, self.ref_start, self.ref_end),
                                            'state':'code',
                                            'priority':0})    
                    to_invoice = self.env['sale.order'] 
                    fini=True
        
        
        return sale_orders.action_view_invoice()
