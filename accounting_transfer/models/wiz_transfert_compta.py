# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import time
import calendar
from dateutil.relativedelta import relativedelta
import base64
#from . import controller_export_csv_order_line
import io
import os
import sys
from odoo.tools import pycompat, misc
#from . import tools_miadi

def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)

class Wizard_transfert_compta(models.TransientModel):
    _name = "wiz.accountingtransfer"
    _description = "Wizard accounting transfer "
    
 #    @api.model
    def _default_start(self):
        #return fields.Date.context_today(self)
        start = datetime.today() + timedelta(days=-7)
        return fields.Date.context_today(self, timestamp=start)

#    @api.model
    def _default_finish(self):
        finish = datetime.today() + timedelta(days=7)
        return fields.Date.context_today(self, timestamp=finish)
    
#    @api.model
    def _get_values(self, valeur):
        """
        Return values for the fields 
        """
        
        val_path_account_transfer = ''
        val_account_file_transfer = ''
        val_writing_file_transfer = ''
        val_mail_accounting = False
        
        #company_id = self.env['res.company']._company_default_get('di.accounting.parameter')
        #val_company_id =company_id.id 
        val_company_id =self._context.get('force_company', self.env.user.company_id.id)
        
        val_name = 'General Settings'
        
        #settings = self.env['di.accounting.parameter'].search([('name','=', val_name), ('company_id','=', val_company_id)])
        #for settings_vals in settings:
        #    val_path_account_transfer = settings_vals.path_account_transfer
        #    val_account_file_transfer = settings_vals.account_file_transfer
        #    val_writing_file_transfer = settings_vals.writing_file_transfer
        #    val_mail_accounting = settings_vals.mail_accounting
            
        
        val_path_account_transfer = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.path_account_transfer')    
        val_account_file_transfer = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.account_file_transfer')
        val_writing_file_transfer = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.writing_file_transfer')
        val_mail_accounting = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.mail_accounting')
            
        if valeur == 'path_account_transfer':
            retour = val_path_account_transfer   
                    
        if valeur == 'account_file_transfer':
            retour = val_account_file_transfer  
                    
        if valeur == 'writing_file_transfer':
            retour = val_writing_file_transfer  
            
        if valeur == 'mail_accounting':
            retour = val_mail_accounting                  
        return retour

    date_start = fields.Date('Start Date', help="Starting date", default=lambda self: self._default_start())
    date_end = fields.Date('End Date', help="Ending date", default=lambda self: fields.Date.today())
    journal_ids = fields.Many2many(comodel_name='account.journal',string="Journals", default=lambda self: self.env['account.journal'].search([('type', 'in', ['sale', 'purchase','cash','bank'])]),required=True)
    path_account_transfer = fields.Char(string='Path For Account Transfer', default=lambda self: self._get_values('path_account_transfer'))
    account_file_transfer = fields.Char(string='File For Account Transfer', default=lambda self: self._get_values('account_file_transfer'))
    writing_file_transfer = fields.Char(string='File For Writing Transfer', default=lambda self: self._get_values('writing_file_transfer'))
    template_id  = fields.Many2one('mail.template', 'Mail',  domain=[('model', '=', 'wiz.transfertcompta')])
    message = fields.Text(string="Information")
    mail_accounting = fields.Boolean(string="Send Email", default=lambda self: self._get_values('mail_accounting'))
    re_transfer = fields.Boolean(string="Re-Transfer", default=False)
    compta_data = fields.Binary('Accounting File', readonly=True)
    filename = fields.Char(string='Filename', size=256, readonly=True)            
    partner_data = fields.Binary('Partner File', readonly=True)
    partner_filename = fields.Char(string='Partner Filename', size=256, readonly=True)            

    #@api.multi
    def send_mail_template(self):   

        '''
        This function opens a window to compose an email, with the  template message loaded by default
        '''
        csv_path = self.path_account_transfer
        account_file = self.account_file_transfer
        writing_file = self.writing_file_transfer
            
        if csv_path is False or csv_path is None:
            csv_path = os.environ.get('LOCALAPPDATA') or os.getcwd()          # c:\odoo\odoo11
        if account_file is None:   
            account_file = 'comptes.txt'
        if writing_file is None:    
            writing_file = 'ecritures.txt'
            
        csv_path = os.path.normpath(csv_path)
        if not csv_path.endswith('\\'):
            csv_path = csv_path + '\\' 
        
         
        writing_f = csv_path + writing_file
        account_f = csv_path + account_file
        attachments_ids = []
        
        if os.path.exists(writing_f):
            with io.open(writing_f, "rb") as wfile:
                byte_data_w = wfile.read()
            
            attachment_w = {
                'name': ("%s" %writing_file),
                'store_fname': writing_file,
                'datas': base64.encodestring(byte_data_w),
                'type': 'binary'
                }
            id_w = self.env['ir.attachment'].create(attachment_w)
            attachments_ids.append(id_w.id)
 
        if os.path.exists(account_f):
            with io.open(account_f, "rb") as afile:
                byte_data_a = afile.read()

            attachment_a = {
                'name': ("%s" %account_file),
                'store_fname': account_file,
                'datas': base64.encodestring(byte_data_a),
                'type': 'binary'
                }
            id_a = self.env['ir.attachment'].create(attachment_a)  
            attachments_ids.append(id_a.id)
        
        email_template = self.env.ref('accounting_transfer.email_template_accounting_transfer')
        email_template.attachment_ids =  False
        #email_template.attachment_ids =  [(4,id_w.id)]
        email_template.attachment_ids = attachments_ids
        
        #'datas': byte_data,
        #data=0
        #'datas': base64.encode(ufile.read(),data),
        
        #files = os.listdir(csv_path)
        #for ufile in files:


        #email_template.send_mail(self.id, raise_exception=False, force_send=True)
        
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.check_object_reference('accounting_transfer', 'email_template_accounting_transfer', True)[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.check_object_reference('mail', 'email_compose_message_wizard_form', True)[1]
        except ValueError:
            compose_form_id = False
        #'attachment_ids':  [(4,id.id)],    
        ctx = {
            'default_model': 'wiz.accountingtransfer',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'attachment_ids':  attachments_ids,
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }  
   
    def di_ecrire_ligne_comptes_ebp(self,auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux, partner_id, name, street, city, zipcode, code_pays, country, phone, mobile,commercial_partner_id):
        ligne_p = ""
        listrow_p = list()
        listrow_ps = list()
        
        partner  = self.env['res.partner'].search([('id', '=',commercial_partner_id),  ])
        doc_partner  = self.env['res.partner'].search([('id', '=',partner_id),  ])
        
        # partner = Customer
        account_customer_id = partner.property_account_receivable_id.id
        account_customer  = self.env['account.account'].search([('id', '=',account_customer_id),  ])
        account_gen_customer_code = account_customer.code
        account_aux_customer_code = partner.di_auxiliary_account_customer or False
            
        # partner = Supplier
        account_supplier_id = partner.property_account_payable_id.id
        account_supplier  = self.env['account.account'].search([('id', '=',account_supplier_id),  ])
        account_gen_supplier_code = account_supplier.code
        account_aux_supplier_code = partner.di_auxiliary_account_supplier or False
            
        if auxiliary_account:
            account_customer_code = account_aux_customer_code
            account_supplier_code = account_aux_supplier_code
            if int(length_account_aux) != 0:
                if (complete_0_aux):
                    if account_customer_code:
                        account_customer_code = account_customer_code.ljust(int(length_account_aux),'0')
                    if account_supplier_code:    
                        account_supplier_code = account_supplier_code.ljust(int(length_account_aux),'0')
                else: 
                    if account_customer_code and len(account_customer_code) > int(length_account_aux):   
                        account_customer_code = account_customer_code[0:int(length_account_aux)]
                    if account_supplier_code and len(account_supplier_code) > int(length_account_aux):  
                        account_supplier_code = account_supplier_code[0:int(length_account_aux)]            
            
        else:
            account_customer_code = account_gen_customer_code
            account_supplier_code = account_gen_supplier_code 
        
            if int(length_account_gen) != 0:
                if (complete_0_gen):
                    if account_customer_code:
                        account_customer_code = account_customer_code.ljust(int(length_account_gen),'0')
                    if account_supplier_code:    
                        account_supplier_code = account_supplier_code.ljust(int(length_account_gen),'0')
                else: 
                    if account_customer_code and len(account_customer_code) > int(length_account_gen):   
                        account_customer_code = account_customer_code[0:int(length_account_gen)]
                        
                    if account_supplier_code and len(account_supplier_code) > int(length_account_gen):  
                        account_supplier_code = account_supplier_code[0:int(length_account_gen)]
                    
        interloc = ""
        f_name =""
        f_street =""
        f_zip =""
        f_city =""
        f_country =""
        f_phone =""
        f_mobile = ""
                
        if name:
            f_name = name[0:60].replace(',', ' ') 
            f_name = self.env['di.tools'].replace_accent(f_name)
                     
        if street:
            f_street = street[0:100].replace(',', ' ')
        if zipcode:
            f_zip = zipcode[0:5]
        if city:
            f_city = city[0:30].replace(',', ' ') 
        if country:
            f_country = country[0:35]           
        if phone:
            f_phone = phone[0:20].replace(',', ' ')
        if mobile:
            f_mobile = mobile[0:20].replace(',', ' ') 
            
        if account_customer_code and doc_partner.customer_rank !=0:
            csv_p_row = ""
            csv_p_row+= "{},".format(account_customer_code[0:15])
            csv_p_row+= "{},".format(f_name[0:60])
            csv_p_row+= "{},".format(f_name[0:30])
            csv_p_row+= "{},".format(f_street[0:100])
            csv_p_row+= "{},".format(f_zip[0:5])
            csv_p_row+= "{},".format(f_city[0:30])
            csv_p_row+= "{},".format(f_country[0:35])
            csv_p_row+= "{},".format(interloc)
            csv_p_row+= "{},".format(f_phone[0:20])
            csv_p_row+= "{},".format(f_mobile[0:20])
           
            ligne_p+="{}\n".format(csv_p_row[:-1])
            #lines.append(([account_customer_code[0:15], f_name[0:60], f_name[0:30], f_street[0:100], f_zip[0:5], f_country[0:35], interloc, f_phone[0:20], f_mobile[0:20]  ]))

            listrow_p.append("{}".format(account_customer_code[0:15]))
            listrow_p.append("{}".format(f_name[0:60]))
            listrow_p.append("{}".format(f_name[0:30]))
            listrow_p.append("{}".format(f_street[0:100]))
            listrow_p.append("{}".format(f_zip[0:5]))
            listrow_p.append("{}".format(f_city[0:35]))
            listrow_p.append("{}".format(f_country[0:35]))
            listrow_p.append("{}".format(interloc))
            listrow_p.append("{}".format(f_phone[0:20]))
            listrow_p.append("{}".format(f_mobile[0:20]))
 
        if account_supplier_code and doc_partner.supplier_rank !=0:
            csv_p_row = ""
            csv_p_row+= "{},".format(account_supplier_code[0:15])
            csv_p_row+= "{},".format(f_name[0:60])
            csv_p_row+= "{},".format(f_name[0:30])
            csv_p_row+= "{},".format(f_street[0:100])
            csv_p_row+= "{},".format(f_zip[0:5])
            csv_p_row+= "{},".format(f_city[0:30])
            csv_p_row+= "{},".format(f_country[0:35])
            csv_p_row+= "{},".format(interloc)
            csv_p_row+= "{},".format(f_phone[0:20])
            csv_p_row+= "{},".format(f_mobile[0:20])
           
            ligne_p+="{}\n".format(csv_p_row[:-1])
            #lines.append(([account_supplier_code[0:15], f_name[0:60], f_name[0:30], f_street[0:100], f_zip[0:5], f_country[0:35], interloc, f_phone[0:20], f_mobile[0:20]  ]))
            listrow_ps.append("{}".format(account_supplier_code[0:15]))
            listrow_ps.append("{}".format(f_name[0:60]))
            listrow_ps.append("{}".format(f_name[0:30]))
            listrow_ps.append("{}".format(f_street[0:100]))
            listrow_ps.append("{}".format(f_zip[0:5]))
            listrow_p.append("{}".format(f_city[0:35]))
            listrow_ps.append("{}".format(f_country[0:35]))
            listrow_ps.append("{}".format(interloc))
            listrow_ps.append("{}".format(f_phone[0:20]))
            listrow_ps.append("{}".format(f_mobile[0:20]))
 

        #return ligne
        return {
            'ligne_p': ligne_p,
            'listrow_p': listrow_p,
            'listrow_ps': listrow_ps,
        }    
   
    def di_ecrire_ligne_ebp(self,auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux, move_name, journal_id, compte_id, move_line_name, date_ecr, date_ech, debit, credit, currency, move_type, ref, compte_anal, partner_id, commercial_partner_id, nb_lig):
        ligne = ""
        listrow = list()
        libelle = ""
        n_piece=""
          
        journal = self.env['account.journal'].browse(journal_id)   
        compte = self.env['account.account'].browse(compte_id)     
        partner  = self.env['res.partner'].search([('id', '=',commercial_partner_id),  ])

        # partner = Customer
        account_customer_id = partner.property_account_receivable_id.id
        account_customer  = self.env['account.account'].search([('id', '=',account_customer_id),  ])
        account_gen_customer_code = account_customer.code
        account_aux_customer_code = partner.di_auxiliary_account_customer or False
            
        # partner = Supplier
        account_supplier_id = partner.property_account_payable_id.id
        account_supplier  = self.env['account.account'].search([('id', '=',account_supplier_id),  ])
        account_gen_supplier_code = account_supplier.code
        account_aux_supplier_code = partner.di_auxiliary_account_supplier or False
        
        compte_gen = compte.code   
        length_account = length_account_gen
        complete_0 = complete_0_gen
                
        if (compte_gen == account_gen_customer_code ) or (compte_gen == account_gen_supplier_code):
            if auxiliary_account:
                if (compte_gen == account_gen_customer_code) and (account_aux_customer_code):
                    compte_gen = account_aux_customer_code
                if (compte_gen == account_gen_supplier_code) and (account_aux_supplier_code):
                    compte_gen = account_aux_supplier_code
                
                length_account = length_account_aux
                complete_0 = complete_0_aux
        
        if int(length_account) != 0:  
            if (complete_0):
                compte_gen = compte_gen.ljust(int(length_account),'0')
                        
            else: 
                if  len(compte_gen) > int(length_account):   
                    compte_gen=compte_gen[0:int(length_account)] 

        #if move_line_name =="/":
        #    if partner.name:
        #        libelle = partner.name
        #else:
        #    if move_line_name:
        #        libelle = move_line_name  
          
        if move_name:
            n_piece = move_name
       
        """    
        if move_type in ('out_refund','in_refund'):
            libelle="Avoir " + n_piece[-10:] + " " + partner.name
        else:
            if move_type in ('out_invoice','in_invoice'):
                libelle="Facture " + n_piece[-10:] + " " + partner.name
            else:    
                if partner.name:       
                    libelle="Piece " + n_piece[-10:] + " " + partner.name
                else:
                    libelle="Piece " + n_piece[-10:]    
                  
        libelle = libelle.replace(',', '.').replace('\n',' ') 
        libelle =  self.env['di.tools'].replace_accent(libelle)
        """
        libelle = self.di_libelle_ecriture (move_type, n_piece, partner)
        libelleAuto = ""
                   
        if debit == 0:
            montant = credit
            sens = "C"
        else:         
            montant = debit
            sens = "D"
        type_tva = "" 
            
#         csv_row = ""
        ligne+= "{},".format(nb_lig)
        ligne+= "{},".format(date_ecr)
        ligne+= "{},".format(journal.code)
        ligne+= "{},".format(compte_gen[0:15])
        ligne+= "{},".format(libelleAuto)
        ligne+= "{},".format(libelle[0:40])
        ligne+= "{},".format(n_piece[-10:])
        ligne+= "{0:.2f},".format(montant)
        ligne+= "{},".format(sens)
        ligne+= "{},".format(date_ech)
        ligne+= "{},".format(type_tva)
        ligne+= "{}".format(currency)
        ligne+= "{}".format("\n")     
        #ligne+="{}\n".format(csv_row[:-1])
        
        listrow.append("{}".format(nb_lig))
        listrow.append("{}".format(date_ecr))
        listrow.append("{}".format(journal_id))
        listrow.append("{}".format(compte_gen[0:15]))
        listrow.append("{}".format(libelleAuto))
        listrow.append("{}".format(libelle[0:40]))
        listrow.append('{}'.format(n_piece[-10:]))
        listrow.append("{0:.2f}".format(montant))
        listrow.append("{}".format(sens))
        listrow.append("{}".format(date_ech))
        listrow.append("{}".format(type_tva))
        listrow.append("{}".format(currency))
            
        #Analytique
        pourc="100.00"
        if compte_anal:
            ligne+= ">"
            ligne+= "{},".format(compte_anal) 
            ligne+= "{},".format(pourc)
            ligne+= "{0:.2f}".format(montant)
            ligne+= "{}".format("\n")
               
            #ligne+="{}\n".format(csv_row[:-1])
        
   
        return ligne.encode("utf-8")
        
        #return {
        #    'ligne': ligne,
        #    'listrow': listrow,
        #}    
        
#    @api.multi

    def di_ecrire_ligne_quadra(self,auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux, move_name, journal_id, compte_id, move_line_name, date_ecr, date_ech, debit, credit, currency, move_type, compte_anal, balance, partner_id, commercial_partner_id, payment_mode):#, di_dos_compt, di_etb_compt):
        ligne="" 
        listrow = list()      
        libelle = ""
        codeLibelle = " "
        n_piece = ""
        ligne_vide=""
        
        #invoice = self.env['account.invoice'].browse(invoice_id)
        #date_fac = invoice.date_invoice.strftime("%d%m%y")
        #DDMMYY
        date_fac = ""
        date_fac = date_ecr[0:4] + date_ecr[-2:]
        date_ech = date_ech[0:4] + date_ech[-2:]
        
        journal = self.env['account.journal'].browse(journal_id)
        partner = self.env['res.partner'].browse(commercial_partner_id)
        compte = self.env['account.account'].browse(compte_id)     
            
        #spé réseau mer, le code compte quadra des tiers est renseigné dans ref
        #if (invoice.type in ('out_invoice','out_refund') and compte.internal_type=='receivable') or (invoice.type in ('in_invoice','in_refund') and compte.internal_type=='payable') : 
        #        if partner.supplier and partner.customer:
        #            if invoice.type in ('in_invoice','in_refund'):
        #                compte_gen = partner.property_account_payable_id.code
        #            else:
        #                compte_gen = partner.property_account_receivable_id.code                    
        #        else:            
        #            if partner.customer:
        #                if partner.ref:          
        #                    compte_gen = partner.ref
        #                else:
        #                    compte_gen=partner.property_account_receivable_id.code
        #            else:
        #                if partner.ref:          
        #                    compte_gen = partner.ref
        #                else:
        #                    compte_gen=partner.property_account_receivable_id.code
        #else:
        #    compte_gen=compte.code
        
        # partner = Customer
        account_customer_id = partner.property_account_receivable_id.id
        account_customer  = self.env['account.account'].search([('id', '=',account_customer_id),  ])
        account_gen_customer_code = account_customer.code
        account_aux_customer_code = partner.di_auxiliary_account_customer or False
            
        # partner = Supplier
        account_supplier_id = partner.property_account_payable_id.id
        account_supplier  = self.env['account.account'].search([('id', '=',account_supplier_id),  ])
        account_gen_supplier_code = account_supplier.code
        account_aux_supplier_code = partner.di_auxiliary_account_supplier or False
        
        compte_gen = compte.code 
        compte_collectif = compte.code  
        length_account = length_account_gen
        complete_0 = complete_0_gen
        type_compte=""
                
        if (compte_gen == account_gen_customer_code ) or (compte_gen == account_gen_supplier_code):
            # COMPTE TIERS
            if auxiliary_account:
                if (compte_gen == account_gen_customer_code) and (account_aux_customer_code):
                    compte_gen = account_aux_customer_code
                    type_compte="1CN"
                if (compte_gen == account_gen_supplier_code) and (account_aux_supplier_code):
                    compte_gen = account_aux_supplier_code
                    type_compte="1FN"
                    
                length_account = length_account_aux
                complete_0 = complete_0_aux
            #else:
            #    if partner.ref:    
            #       compte_gen = partner.ref 
                   
            
        
        if int(length_account) != 0:  
            if (complete_0):
                compte_gen = compte_gen.ljust(int(length_account),'0')
                        
            else:  
                if  len(compte_gen) > int(length_account):  
                    compte_gen=compte_gen[0:int(length_account)] 

        
        if type_compte!= "":
            # Ecriture ligne TYPE = C
            ce1 = "C"
            
            street = partner.street or ""
            street2 = partner.street2 or ""
            phone = partner.phone or ""
            zipcode = partner.zip or ""
            city = partner.city or ""
            ville = zipcode + " " + city 
            
            ligne+="{}".format(ce1.ljust(1)[0])
            ligne+= "{}".format(compte_gen.ljust(8)[0:8])
            ligne+= "{}".format(partner.name.ljust(30)[0:30])
            ligne+= "{}".format("       +000000000000+000000000000+000000000000+000000000000")
            ligne+= "{}".format(compte_collectif.ljust(8)[0:8])
            ligne+= "{}".format(street.ljust(30)[0:30])
            ligne+= "{}".format(street2.ljust(30)[0:30])
            ligne+= "{}".format(ville.ljust(30)[0:30])
            ligne+= "{}".format(phone.ljust(20)[0:20])
            ligne+= "{}".format(type_compte.ljust(3)[0:3])
            ligne+= "{}".format(ligne_vide.ljust(95)[0:95])
            ligne+= "{}".format("\n")
           
        if move_name:
            n_piece = move_name[-10:]# n° pièce limité à 10 caractères sur quadra -> paramétrage de séquence sur 10
        
        #if move_line_name == "/":
        #    if partner.name:
        #        libelle = partner.name
        #else:
        #    if move_line_name:
        #        libelle = move_line_name  
       
        """       
        if move_type in ('out_refund','in_refund'):
            libelle="Avoir " + n_piece + " " + partner.name
            codeLibelle = "A"
        else:
            if move_type in ('out_invoice','in_invoice'):
                libelle="Facture " + n_piece + " " + partner.name
                codeLibelle = "F"
            else: 
                if type_compte!= "":          
                    libelle="Piece " + n_piece + " " + partner.name
                else:
                    libelle="Piece " + n_piece    
        
        libelle = self.env['di.tools'].replace_accent(libelle)
        """
        libelle = self.di_libelle_ecriture (move_type, n_piece, partner)

        if move_type in ('out_refund','in_refund'):
            codeLibelle = "A"
        else:
            if move_type in ('out_invoice','in_invoice'):
                codeLibelle = "F"
                
        montant=0.0     
        di_balance    = abs(balance) # on prend balance car déjà formaté/arrondi comme il faut  
        if debit == 0:
            # crédit
            montant = round(di_balance*100.0,2) #pas de décimale
            sens = "C"
        else:
            # débit         
            montant = round(di_balance*100.0,2) #pas de décimale
            sens = "D"
        
        ce1 = "M"
        
        if montant >=0:
            signe="+"
        else:
            signe="-"
        montant_int = int(montant)
        montant_str = str(montant_int) 
            
        ecrno = ""
        ecrlg = ""
        axe1 = ""
        axe2 = ""
        axe3 = ""
        axe4 = ""
        cp = ""
        reg = ""
        lett = ""
        point = ""
        lot = ""
        chqno = ""
        regtyp = ""
        mtbis = ""
        lettdt = ""
        pointdt = ""
        ecrvalno = ""
        devp = ""
        cptcol = ""
        natpai = ""


        #écriture de la ligne avec longueurs fixes, préfixer avec des 0 pour les numériques
        csv_row = ""
        ligne+="{}".format(ce1.ljust(1)[0])
        ligne+= "{}".format(compte_gen.ljust(8)[0:8])
        ligne+= "{}".format(journal.code.ljust(5)[0:5])
        ligne+= "{}".format(date_fac.ljust(6)[0:6])
        ligne+= "{}".format(codeLibelle.ljust(1)[0])
        ligne+= "{}".format("                    ")
        ligne+= "{}".format(sens.ljust(1)[0])
        ligne+= "{}".format(signe.ljust(1)[0])  
        ligne+= "{}".format(montant_str.zfill(12)[0:12]) 
        ligne+= "{}".format("        ")               
        ligne+= "{}".format(date_ech.ljust(6)[0:6])
        ligne+= "{}".format("                              ")      
        ligne+= "{}".format(n_piece.ljust(8)[-8:])
        ligne+= "{}".format(currency.ljust(3)[0:3])
        ligne+= "{}".format(journal.code.ljust(5)[0:5])
        ligne+= "{}".format(" ")              
        ligne+= "{}".format(libelle.ljust(32)[0:32])
        ligne+= "{}".format(n_piece.ljust(10))
        ligne+= "{}".format("          ")    
        ligne+= "{}".format(signe.ljust(1)[0])
        ligne+= "{}".format(montant_str.zfill(12)[0:12])
        ligne+= "{}".format("\n")  
        
        # analytique
        pourc="100.00"
        if compte_anal:
            ligne+="{}".format("I10000")
            ligne+= "{}".format(signe.ljust(1)[0])  
            ligne+= "{}".format(montant_str.zfill(12)[0:12]) 
            ligne+= "{}".format(compte_anal.ljust(10)[0:10])
            ligne+= "{}".format(ligne_vide.ljust(10)[0:10])
            ligne+= "{}".format("\n")
        
        listrow.append("{}".format(ce1.ljust(1)[0]))
        listrow.append("{}".format(compte_gen.ljust(8)[0:8]))
        listrow.append("{}".format(journal.code.ljust(5)[0:5]))
        listrow.append("{}".format(date_fac.ljust(6)[0:6]))
        listrow.append("{}".format("                     "))
        listrow.append("{}".format(sens.ljust(1)[0]))
        listrow.append("{}".format(signe.ljust(1)[0]))
        listrow.append("{}".format(montant_str.zfill(12)[0:12]))
        listrow.append("{}".format("        "))         
        listrow.append("{}".format(date_ech.ljust(6)[0:6]))
        listrow.append("{}".format("                              ") )     
        listrow.append("{}".format(n_piece.ljust(8)))
        listrow.append("{}".format(currency.ljust(3)[0:3]))
        listrow.append("{}".format(journal.code.ljust(5)[0:5]))
        listrow.append("{}".format(" ") )             
        listrow.append("{}".format(libelle.ljust(32)[0:32]))
        listrow.append("{}".format(n_piece.ljust(8)))
        listrow.append("{}".format("            "))    
        listrow.append("{}".format(signe.ljust(1)[0]))
        listrow.append("{}".format(montant_str.zfill(12)[0:12]))
        #listrow.append("{}".format("\n"))  
        
        return ligne.encode("utf-8")
    
        #return {
        #    'ligne' : csv_row,
        #    'listrow': listrow,
        #}    

    def di_ecrire_compte_sage(self,auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux, partner_id, commercial_partner_id, nb_lig_tiers):
        ligne = ""
        listrow = list()
        libelle = ""
        n_piece=""
        tabMPCT=["" for i in range(97)]
          
        date_today = datetime.today().strftime('%d%m%Y')
          
        partner  = self.env['res.partner'].search([('id', '=',commercial_partner_id),  ])

        # partner = Customer
        account_customer_id = partner.property_account_receivable_id.id
        account_customer  = self.env['account.account'].search([('id', '=',account_customer_id),  ])
        account_gen_customer_code = account_customer.code
        account_aux_customer_code = partner.di_auxiliary_account_customer or ""
            
        # partner = Supplier
        account_supplier_id = partner.property_account_payable_id.id
        account_supplier  = self.env['account.account'].search([('id', '=',account_supplier_id),  ])
        account_gen_supplier_code = account_supplier.code
        account_aux_supplier_code = partner.di_auxiliary_account_supplier or ""
        
        length_account = length_account_gen
        complete_0 = complete_0_gen
        compte_aux = "" 
        type_aux = "" 
 
        name_partner = self.env['di.tools'].replace_accent(partner.name) or ""
        street = self.env['di.tools'].replace_accent(partner.street) or ""
        street2 = self.env['di.tools'].replace_accent(partner.street2) or ""
        phone = self.env['di.tools'].replace_accent(partner.phone) or ""
        mobile = self.env['di.tools'].replace_accent(partner.mobile) or ""
        zipcode = self.env['di.tools'].replace_accent(partner.zip) or ""
        city = self.env['di.tools'].replace_accent(partner.city) or ""
        ville = zipcode + " " + city 
        pays = self.env['di.tools'].replace_accent(partner.country_id.name) or ""
        
        
        tabMPCT[1] = name_partner[0:69]
        tabMPCT[5] = name_partner[0:17]
        tabMPCT[7] = street[0:35]
        tabMPCT[8] = street2[0:35]
        tabMPCT[9] = zipcode[0:9]
        tabMPCT[10] = city[0:35]
        tabMPCT[12] = pays[0:35]
        tabMPCT[53] = date_today[0:4] + date_today[-2:]
        tabMPCT[43] = phone[0:21]
        tabMPCT[44] = mobile[0:21]
           
        tabMPCT[32] ="1"
        tabMPCT[33] ="1"
        tabMPCT[37] ="0"
        tabMPCT[38] ="1"
        tabMPCT[39] ="1"
        tabMPCT[46] ="1"
        tabMPCT[47] ="1"
            
        #  partner = Customer        
        if account_gen_customer_code != "" and account_aux_customer_code != "":
            compte_gen = account_gen_customer_code
            compte_aux = account_aux_customer_code
            type_aux = "0" 

            if int(length_account_aux) != 0:  
                if (complete_0_aux):
                    compte_aux = compte_aux.ljust(int(length_account_aux),'0')
                        
                else: 
                    if  len(compte_aux) > int(length_account_aux):   
                        compte_aux = compte_gen[0:int(length_account_aux)] 
            
            if int(length_account) != 0:  
                if (complete_0):
                    compte_gen = compte_gen.ljust(int(length_account),'0')
                        
                else: 
                    if  len(compte_gen) > int(length_account):   
                        compte_gen = compte_gen[0:int(length_account)] 
 
            tabMPCT[0] = compte_aux[0:17].upper()
            tabMPCT[2] = type_aux
            tabMPCT[3] = compte_gen[0:13]
            tabMPCT[96] = compte_gen[0:13]
         
            
            if nb_lig_tiers == 1:
                ligne+= "#VER 14"
                ligne+= "{}".format("\r\n")
                ligne+= "#DEV EUR"
                ligne+= "{}".format("\r\n")
                nb_lig_tiers += 1

            ligne+= "#MPCT"
            ligne+= "{}".format("\r\n") 
            for x in range(0,97):
               ligne+= "{}".format(tabMPCT[x])
               ligne+= "{}".format("\r\n")
            

         #  partner = Supplier        
        if account_gen_supplier_code != "" and account_aux_supplier_code != "":
            compte_gen = account_gen_supplier_code
            compte_aux = account_aux_supplier_code
            type_aux = "1" 

            if int(length_account_aux) != 0:  
                if (complete_0_aux):
                    compte_aux = compte_aux.ljust(int(length_account_aux),'0')
                        
                else: 
                    if  len(compte_aux) > int(length_account_aux):   
                        compte_aux = compte_gen[0:int(length_account_aux)] 
            
            if int(length_account) != 0:  
                if (complete_0):
                    compte_gen = compte_gen.ljust(int(length_account),'0')
                        
                else: 
                    if  len(compte_gen) > int(length_account):   
                        compte_gen = compte_gen[0:int(length_account)] 
            
            
            tabMPCT[0] = compte_aux[0:17].upper()
            tabMPCT[2] = type_aux
            tabMPCT[3] = compte_gen[0:13]
            tabMPCT[96] = compte_gen[0:13]
           
            if nb_lig_tiers == 1:
                ligne+= "#VER 14"
                ligne+= "{}".format("\r\n")
                ligne+= "#DEV EUR"
                ligne+= "{}".format("\r\n")
                nb_lig_tiers += 1

            ligne+= "#MPCT"
            ligne+= "{}".format("\r\n") 
            for x in range(0,97):
               ligne+= "{}".format(tabMPCT[x])
               ligne+= "{}".format("\r\n")
        
        return ligne.encode("utf-8")


    def di_ecrire_ligne_sage(self,auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux, move_name, journal_id, compte_id, move_line_name, date_ecr, date_ech, debit, credit, currency, move_type, ref, compte_anal, partner_id, commercial_partner_id, payment_mode, nb_lig):
        ligne = ""
        listrow = list()
        libelle = ""
        n_piece=""
        tabMPCT=["" for i in range(97)]
        tabMECG=["" for i in range(37)]
          
        journal = self.env['account.journal'].browse(journal_id)   
        compte = self.env['account.account'].browse(compte_id)     
        partner  = self.env['res.partner'].search([('id', '=',commercial_partner_id),  ])

        # partner = Customer
        account_customer_id = partner.property_account_receivable_id.id
        account_customer  = self.env['account.account'].search([('id', '=',account_customer_id),  ])
        account_gen_customer_code = account_customer.code
        account_aux_customer_code = partner.di_auxiliary_account_customer or False
            
        # partner = Supplier
        account_supplier_id = partner.property_account_payable_id.id
        account_supplier  = self.env['account.account'].search([('id', '=',account_supplier_id),  ])
        account_gen_supplier_code = account_supplier.code
        account_aux_supplier_code = partner.di_auxiliary_account_supplier or False
        
        compte_gen = compte.code   
        length_account = length_account_gen
        complete_0 = complete_0_gen
        compte_aux = "" 
        type_aux = "" 
                
        if (compte_gen == account_gen_customer_code ) or (compte_gen == account_gen_supplier_code):
            if auxiliary_account:
                if (compte_gen == account_gen_customer_code) and (account_aux_customer_code):
                    compte_aux = account_aux_customer_code
                    type_aux = "0" 
                if (compte_gen == account_gen_supplier_code) and (account_aux_supplier_code):
                    compte_aux = account_aux_supplier_code
                    type_aux = "1" 
                    
                if int(length_account_aux) != 0:  
                    if (complete_0_aux):
                        compte_aux = compte_aux.ljust(int(length_account_aux),'0')
                        
                    else: 
                        if  len(compte_aux) > int(length_account_aux):   
                            compte_aux = compte_gen[0:int(length_account_aux)] 
            
            """  
            name_partner = partner.name or ""
            street = partner.street or ""
            street2 = partner.street2 or ""
            phone = partner.phone or ""
            mobile = partner.mobile or ""
            zipcode = partner.zip or ""
            city = partner.city or ""
            ville = zipcode + " " + city 
            pays = partner.country_id.name or ""
        
            tabMPCT[0] = compte_aux[0:17]
            tabMPCT[1] = name_partner[0:69]
            tabMPCT[2] = type_aux
            tabMPCT[3] = compte_gen[0:13]
            tabMPCT[5] = name_partner[0:17]
            tabMPCT[7] = street[0:35]
            tabMPCT[8] = street2[0:35]
            tabMPCT[9] = zipcode[0:9]
            tabMPCT[10] = city[0:35]
            tabMPCT[12] = pays[0:35]
            #tabMPCT[31] = compte_gen[0:13]
            tabMPCT[53] = date_ecr[0:4] + date_ecr[-2:]
            #tabMPCT[49] = date_ecr[0:4] + date_ecr[-2:]
            tabMPCT[43] = phone[0:21]
            tabMPCT[44] = mobile[0:21]
            tabMPCT[96] = compte_gen[0:13]
            
            tabMPCT[32] ="1"
            tabMPCT[33] ="1"
            tabMPCT[37] ="0"
            tabMPCT[38] ="1"
            tabMPCT[39] ="1"
            tabMPCT[46] ="1"
            tabMPCT[47] ="1"
            """
        if int(length_account) != 0:  
            if (complete_0):
                compte_gen = compte_gen.ljust(int(length_account),'0')
                        
            else: 
                if  len(compte_gen) > int(length_account):   
                    compte_gen = compte_gen[0:int(length_account)] 

        #if move_line_name =="/":
        #    if partner.name:
        #        libelle = partner.name
        #else:
        #    if move_line_name:
        #        libelle = move_line_name  
          
        if move_name:
            n_piece = move_name
         
        n_piece = self.env['di.tools'].replace_car(n_piece)
        n_piece = self.env['di.tools'].replace_accent(n_piece)  
        
        """    
        if move_type in ('out_refund','in_refund'):
            libelle="Avoir " + n_piece[-10:] + " " + partner.name
        else:
            if move_type in ('out_invoice','in_invoice'):
                libelle="Facture " + n_piece[-10:] + " " + partner.name
            else: 
                if partner.name:          
                    libelle="Piece " + n_piece[-10:] + " " + partner.name
                else:
                    libelle="Piece " + n_piece[-10:]    
                    
        libelle = self.env['di.tools'].replace_accent(libelle)    
        libelle = libelle.replace(',', '.').replace('\n',' ') 
        """
        libelle = self.di_libelle_ecriture (move_type, n_piece, partner)
                   
        if debit == 0:
            montant = credit
            sens = 1
        else:         
            montant = debit
            sens = 0
        type_tva = "" 
 
        tabMECG[0] = journal.code[0:6]
        tabMECG[1] = date_ecr[0:4] + date_ecr[-2:]
        tabMECG[3] = n_piece[0:13]
        tabMECG[4] = n_piece[0:17]
        tabMECG[6] = compte_gen[0:13]
        tabMECG[8] = compte_aux[0:17].upper()
        tabMECG[10] = libelle[0:69]
        tabMECG[11] = payment_mode
        tabMECG[12] = date_ech[0:4] + date_ech[-2:]
        tabMECG[14] = 0
        tabMECG[16] = sens
        tabMECG[17] = montant
       
        if nb_lig == 1:
            ligne+= "#VER 14"
            ligne+= "{}".format("\r\n")
            ligne+= "#DEV EUR"
            ligne+= "{}".format("\r\n")
         
#        if compte_aux != "":
#           ligne+= "#MPCT"
#           ligne+= "{}".format("\r\n") 
#           for x in range(0,97):
#               ligne+= "{}".format(tabMPCT[x])
#               ligne+= "{}".format("\r\n")
            
        ligne+= "#MECG"
        ligne+= "{}".format("\r\n")
        
        for x in range(0,37):
            ligne+= "{}".format(tabMECG[x])
            ligne+= "{}".format("\r\n")
            
   
        #Analytique
        pourc="100.00"
        if compte_anal:
            ligne+= "#MECA"
            ligne+= "{}".format("\r\n")
            ligne+= "1"
            ligne+= "{}".format("\r\n")
            ligne+= "{}".format(compte_anal[0:13].upper())
            ligne+= "{}".format("\r\n") 
            ligne+= "{0:.2f}".format(montant)
            ligne+= "{}".format("\r\n")
            ligne+= "{}".format("\r\n")
           
   
        return ligne.encode("utf-8")
    
    def di_ecrire_ligne_sage_Fin(self):
        ligne= "#FIN"
        ligne+= "{}".format("\n")
        return ligne.encode("utf-8")
     
     
    def di_libelle_ecriture (self, move_type, n_piece, partner):
        lib=""
        codeLib=" "
        if move_type in ('out_refund','in_refund'):
            lib="Avoir " + n_piece[-10:] + " " + partner.name
            
        else:
            if move_type in ('out_invoice','in_invoice'):
                lib="Facture " + n_piece[-10:] + " " + partner.name
                
            else:    
                if partner.name:       
                    lib="Piece " + n_piece[-10:] + " " + partner.name
                else:
                    lib="Piece " + n_piece[-10:]    
                  
        lib = lib.replace(',', '.').replace('\n',' ') 
        lib =  self.env['di.tools'].replace_accent(lib)
        
        return lib
            
            
    def transfert_compta(self, **kw):  
        #s = s[ beginning : beginning + LENGTH]
        #date_d =  self.date_start[0:4] + self.date_start[5:7] + self.date_start[8:10] 
        #date_f =  self.date_end[0:4]+ self.date_end[5:7] + self.date_end[8:10] 
        date_d=self.date_start.strftime('%Y%m%d')
        date_f=self.date_end.strftime('%Y%m%d')
        query_args = {'date_start' : date_d,'date_end' : date_f}
        nb_lig = 0
        
        # General Settings
        #company_id = self.env['res.company']._company_default_get('di.accounting.parameter')
        #val_company_id =company_id.id 
        val_company_id = self._context.get('force_company', self.env.user.company_id.id)
        
        val_name = 'General Settings'

        auxiliary_account = False
        length_account_gen = 0
        length_account_aux = 0
        complete_0_gen = False
        complete_0_aux = False
        type_accounting = "EBP"
        
        #settings = self.env['di.accounting.parameter'].search([('name','=', val_name), ('company_id','=', val_company_id)])
        #if settings:
        #    auxiliary_account = settings.auxiliary_accounting
        #    length_account_gen = settings.length_account_general
        #    length_account_aux = settings.length_account_auxiliary
        #    complete_0_gen = settings.complete_0_account_general or False
        #    complete_0_aux = settings.complete_0_account_general or False
        #    type_accounting = settings.type_accounting or "EBP"
        #else:
        #    auxiliary_account = False
        #    length_account_gen = 0
        #    length_account_aux = 0
        #    complete_0_gen = False
        #    complete_0_aux = False
        #    type_accounting = "EBP"
        
        
        auxiliary_account = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.auxiliary_accounting')
        length_account_gen = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.length_account_general')
        length_account_aux = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.length_account_auxiliary')
        complete_0_gen = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.complete_0_account_general')
        complete_0_aux = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.complete_0_account_auxiliary')
        type_accounting = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.type_accounting')


        #csv_path = self.path_account_transfer
        account_file = self.account_file_transfer
        writing_file = self.writing_file_transfer
            
        #if csv_path is None:
        #   csv_path = os.environ.get('LOCALAPPDATA') or os.getcwd()          
        if account_file is None:   
            account_file = 'comptes.txt'
        if writing_file is None:    
            writing_file = 'ecritures.txt'
         
        # Invoice File
        compta_file = io.BytesIO()
        
        # Account File
        partner_file = io.BytesIO()
         
        csv_p = ""
        ligne_p = ""
        
        sql_p = """SELECT distinct am.partner_id, res_partner.name,
                res_partner.street, res_partner.city, res_partner.zip,
                res_country.code as code_pays, res_country.name as country,
                res_partner.phone, res_partner.mobile, am.company_id, am.commercial_partner_id
                from account_move as am
                INNER JOIN res_partner on res_partner.id = am.commercial_partner_id 
                INNER JOIN res_country on res_country.id = res_partner.country_id 
                WHERE am.state = 'posted' 
                AND to_char(am.date,'YYYYMMDD') BETWEEN %s AND %s
                AND am.company_id = %s
                AND am.journal_id IN %s
                ORDER BY am.partner_id"""
                
        self.env.cr.execute(sql_p, (date_d,  date_f, val_company_id, tuple(self.journal_ids.ids),))
        
        nb_lig_tiers = 0
        ids_p = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]) for r in self.env.cr.fetchall()]
        for partner_id, name, street, city, zipcode, code_pays, country, phone, mobile, company, commercial_partner_id in ids_p:
            if type_accounting == "EBP":
                nb_lig_tiers +=1
                ret_p = self.di_ecrire_ligne_comptes_ebp(auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux,partner_id, name, street, city, zipcode, code_pays, country, phone, mobile, commercial_partner_id)
            
                ligne_p = ret_p['ligne_p']
                listrow_p = ret_p['listrow_p']      # partner : customer
                listrow_ps = ret_p['listrow_ps']    # partner : supplier
            
                csv_p+= ligne_p
            
                w_p = pycompat.csv_writer(partner_file, delimiter=',')
                w_p.writerow(listrow_p)
                if len(listrow_ps) !=0:
                    w_p.writerow(listrow_ps)
                        
            if type_accounting == "SAGE":
                nb_lig_tiers +=1
                listrow = self.di_ecrire_compte_sage(auxiliary_account, length_account_gen, length_account_aux, complete_0_gen, complete_0_aux, partner_id, commercial_partner_id, nb_lig_tiers)
                compta_file.write(listrow) 
                nb_lig = 1
                
        # Transfer Invoices

        sql = """SELECT am.name as move_name, account_journal.id as journal, account_account.id as compte,
                am.partner_id as partner, am.commercial_partner_id as commercial_partner, account_account.name as move_line_name,
                to_char(am.date,'DDMMYYYY') as date_ecr,
                CASE WHEN aml.date_maturity IS NULL THEN '' ELSE to_char(aml.date_maturity,'DDMMYYYY') END  as date_ech,
                res_currency.name as currency, aml.ref as ref, aaa.code as compte_anal, am.move_type,
                sum(aml.debit), sum(aml.credit), sum(aml.balance), CASE WHEN pm.di_code IS NULL THEN '' ELSE pm.di_code END as mode_payment
                , aml.id as num_lig, am.id as num_doc
                FROM account_move_line as aml
                INNER JOIN account_move as am on am.id = aml.move_id
                INNER JOIN account_journal on account_journal.id = am.journal_id
                INNER JOIN res_currency on res_currency.id = am.currency_id
                --INNER JOIN res_partner on res_partner.id = am.commercial_partner_id 
                INNER JOIN account_account on account_account.id = aml.account_id 
                LEFT JOIN account_analytic_account as aaa on aaa.id = aml.analytic_account_id 
                
                LEFT JOIN account_payment_mode as pm on pm.id = aml.payment_mode_id 
                WHERE am.state = 'posted' AND aml.balance <> 0 AND aml.account_id is not null 
                AND to_char(am.date,'YYYYMMDD') BETWEEN %s AND %s
                AND  aml.company_id = %s 
                AND am.journal_id IN %s 
                AND CASE WHEN aml.di_transfer_accounting IS NULL THEN False ELSE aml.di_transfer_accounting END is %s
                group by am.name, account_journal.id, account_account.id,
                am.partner_id, am.commercial_partner_id, account_account.name, am.date, 
                aml.date_maturity, res_currency.name, aml.ref, aaa.code, am.move_type, pm.di_code 
                , aml.id, am.id 
                ORDER BY account_journal.code, am.name, account_account.id"""
                
        sql = """SELECT am.name as move_name, account_journal.id as journal, account_account.id as compte,
                am.partner_id as partner, am.commercial_partner_id as commercial_partner, account_account.name as move_line_name,
                to_char(am.date,'DDMMYYYY') as date_ecr,
                CASE WHEN aml.date_maturity IS NULL THEN '' ELSE to_char(aml.date_maturity,'DDMMYYYY') END  as date_ech,
                res_currency.name as currency, aml.ref as ref, aaa.code as compte_anal, am.move_type,
                round(aml.debit,2) as debit, round(aml.credit,2) as credit, round(aml.balance,2) as balance, 
                CASE WHEN pm.di_code IS NULL THEN '' ELSE pm.di_code END as mode_payment
                , aml.id as num_lig, am.id as num_doc
                
                FROM account_move_line as aml
                INNER JOIN account_move as am on am.id = aml.move_id
                INNER JOIN account_journal on account_journal.id = am.journal_id
                INNER JOIN res_currency on res_currency.id = am.currency_id
                INNER JOIN account_account on account_account.id = aml.account_id 
                LEFT JOIN account_analytic_account as aaa on aaa.id = aml.analytic_account_id 
                LEFT JOIN account_payment_mode as pm on pm.id = aml.payment_mode_id 

                WHERE am.state = 'posted' AND aml.balance <> 0 AND aml.account_id is not null 
                AND to_char(am.date,'YYYYMMDD') BETWEEN %s AND %s
                AND  aml.company_id = %s 
                AND am.journal_id IN %s 
                AND CASE WHEN aml.di_transfer_accounting IS NULL THEN False ELSE aml.di_transfer_accounting END is %s
                
                ORDER BY account_journal.code, am.name, account_account.id"""
                
        self.env.cr.execute(sql, (date_d,  date_f, val_company_id, tuple(self.journal_ids.ids),self.re_transfer,))
        
        csv = ""
        ligne = ""
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16], r[17]) for r in self.env.cr.fetchall()]
        for  move_name, journal_id, compte_id, partner_id, commercial_partner_id, move_line_name, date_ecr, date_ech, currency, ref, compte_anal, move_type, debit, credit, balance, payment_mode,num_lig,num_doc  in ids:
            nb_lig +=1
            listrow = list()
            
            if type_accounting == "QUADRA":
                listrow = self.di_ecrire_ligne_quadra(auxiliary_account, length_account_gen, length_account_aux, complete_0_gen, complete_0_aux, move_name, journal_id, compte_id, move_line_name, date_ecr, date_ech, debit, credit, currency, move_type, compte_anal, balance, partner_id, commercial_partner_id, payment_mode)
                compta_file.write(listrow)
            else:
                if type_accounting == "SAGE":
                    # SAGE
                    listrow = self.di_ecrire_ligne_sage(auxiliary_account, length_account_gen, length_account_aux, complete_0_gen, complete_0_aux, move_name, journal_id, compte_id, move_line_name, date_ecr, date_ech, debit, credit, currency, move_type, ref, compte_anal, partner_id, commercial_partner_id, payment_mode, nb_lig)
                    compta_file.write(listrow)
                    nb_lig_tiers = 0
                else:    
                    # EBP
                    listrow = self.di_ecrire_ligne_ebp(auxiliary_account, length_account_gen, length_account_aux, complete_0_gen, complete_0_aux, move_name, journal_id, compte_id, move_line_name, date_ecr, date_ech, debit, credit, currency, move_type, ref, compte_anal, partner_id, commercial_partner_id, nb_lig)
                    compta_file.write(listrow)
                #w = pycompat.csv_writer(compta_file, delimiter=',')
                #w.writerow(listrow)
            
            #ligne = ret['ligne']
            #listrow = ret['listrow']
            
            #csv+= ligne
            #w.writerow(listrow)    
            
            #flag de l'écriture exportée 
            line = self.env['account.move.line'].browse(num_lig)
            line.update({'di_transfer_accounting': True})
            
            move = self.env['account.move'].browse(num_doc)
            transfer_lines = move.line_ids.filtered(lambda line: line.di_transfer_accounting)
            move.update({'di_transfer_lines_count': len(transfer_lines) })
        
        if type_accounting == "SAGE" and nb_lig != 0:
            listrow = self.di_ecrire_ligne_sage_Fin()
            compta_file.write(listrow)
            
        if nb_lig == 0:
            return {'type': 'ir.actions.act_window_close'} 
        else:    
            
            #flag des écritures exportées    
            sql = """SELECT aml.id, aml.move_id
                from account_move_line as aml
                INNER JOIN account_move as am on am.id = aml.move_id
                INNER JOIN account_journal on account_journal.id = am.journal_id
                INNER JOIN res_currency on res_currency.id = am.currency_id
                --INNER JOIN res_partner on res_partner.id = am.commercial_partner_id 
                INNER JOIN account_account on account_account.id = aml.account_id                
                WHERE am.state = 'posted'  AND aml.balance <> 0 AND aml.account_id is not null 
                AND to_char(am.date,'YYYYMMDD') BETWEEN %s AND %s
                AND  aml.company_id = %s 
                AND am.journal_id IN %s
                AND CASE WHEN aml.di_transfer_accounting IS NULL THEN False ELSE aml.di_transfer_accounting END is %s               
                ORDER BY account_journal.id, am.name, account_account.id"""

            """
            self.env.cr.execute(sql, (date_d, date_f, val_company_id, tuple(self.journal_ids.ids),self.re_transfer,))
            ids = [(r[0], r[1]) for r in self.env.cr.fetchall()]
            for id, moveid in ids:    
                line = self.env['account.move.line'].browse(id)
                line.update({'di_transfer_accounting': True})
                
                move = self.env["account.move"].search([("id", "=",moveid)] )
                transfer_lines = move.line_ids.filtered(lambda line: line.di_transfer_accounting)
                move.update({'di_transfer_lines_count': len(transfer_lines) })
            """
            
            if self.mail_accounting:
                # send EMail
                #return self.send_mail_template()
                attachments_ids = []
                comptavalue = compta_file.getvalue()
                partnervalue = partner_file.getvalue()  
                if comptavalue is not None:
                    attachment_w = {
                        'name': ("%s" %writing_file),
                        'store_fname': writing_file,
                        'datas': base64.encodestring(comptavalue),
                        'type': 'binary'
                    }
                    id_w = self.env['ir.attachment'].create(attachment_w)
                    attachments_ids.append(id_w.id)
 
                if (partnervalue is not None and nb_lig_tiers !=0):
                    attachment_a = {
                        'name': ("%s" %account_file),
                        'store_fname': account_file,
                        'datas': base64.encodestring(partnervalue),
                        'type': 'binary'
                    }
                    id_a = self.env['ir.attachment'].create(attachment_a)  
                    attachments_ids.append(id_a.id)
        
                email_template = self.env.ref('accounting_transfer.email_template_accounting_transfer')
                email_template.attachment_ids =  False
        
                email_template.attachment_ids = attachments_ids
        
                ir_model_data = self.env['ir.model.data']
                try:
                    template_id = ir_model_data.check_object_reference('accounting_transfer', 'email_template_accounting_transfer', True)[1]
                except ValueError:
                    template_id = False
                try:
                    compose_form_id = ir_model_data.check_object_reference('mail', 'email_compose_message_wizard_form', True)[1]
                except ValueError:
                    compose_form_id = False

                ctx = {
                    'default_model': 'wiz.accountingtransfer',
                    'default_res_id': self.ids[0],
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id,
                    'default_composition_mode': 'comment',
                    'attachment_ids':  attachments_ids,
                    'force_email': True
                    }
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'mail.compose.message',
                    'views': [(compose_form_id, 'form')],
                    'view_id': compose_form_id,
                    'target': 'new',
                    'context': ctx,
                }          
        
            else:
                #téléchargement du fichier
                """
                view_id = self.env["ir.model.data"].check_object_reference("accounting_transfer", "wiz_transfert_compta_step2", True)
                self.message = ("%s %s %s %s") % ("Create Accounting transfer for ",nb_lig, " lines. Sur ", csv_path )
                return {"type":"ir.actions.act_window",
                    "view_mode":"form",
                    "view_type":"form",
                    "views":[(view_id[1], "form")],
                    "res_id":self.id,
                    "target":"new",
                    "res_model":"wiz.accountingtransfer"                
                    } 
                   
                """
                comptavalue = compta_file.getvalue()
                partnervalue = partner_file.getvalue()
            
                self.write({
                    'compta_data': base64.encodestring(comptavalue),            
                    'filename': writing_file,
                    'partner_data': base64.encodestring(partnervalue),            
                    'partner_filename': account_file,

                })
                compta_file.close()
            
                action_writing = {
                    'name': 'miadi_transfert_compta',
                    'type': 'ir.actions.act_url',
                    'url': "web/content/?model=wiz.accountingtransfer&id=" + str(self.id) + "&filename_field=filename&field=compta_data&download=true&filename=" + self.filename,
                    'target': 'self',
                    }
                action_partner = {
                    'name': 'miadi_transfert_compta_partner',
                    'type': 'ir.actions.act_url',
                    'url': "web/content/?model=wiz.accountingtransfer&id=" + str(self.id) + "&filename_field=partner_filename&field=partner_data&download=true&filename=" + self.partner_filename,
                    'target': 'self',
                    }
                action = {
                    'name': 'miadi_transfert_compta',
                    'type': 'ir.actions.act_url',
                    'url': "web/content/?model=wiz.accountingtransfer&id=" + str(self.id) + "&filename_field=filename&field=compta_data&download=true&filename=" + self.filename + "&filename_field=partner_filename&field=partner_data&download=true&filename=" + self.partner_filename,
                    'target': 'self',
                    }

            
                return action_writing
                #return { 
                #    'action_w': action_writing,
                #    'action_p':action_partner,
                #    }
 


 