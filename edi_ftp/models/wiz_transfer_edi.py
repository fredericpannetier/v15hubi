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
import string
import re
from odoo.tools import pycompat, misc
from ftplib import FTP
from odoo.exceptions import UserError, ValidationError
#from win32inetcon import IDSI_FLAG_KEEP_ALIVE


def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)

class Wizard_ftp_edi(models.TransientModel):
    _name = "wiz.edi.ftp"
    _description = "Wizard EDI FTP"
    
#    @api.model
    def _default_start(self):
        start = datetime.today() + timedelta(days=-7)
        return fields.Date.context_today(self, timestamp=start)

#    @api.model
    def _default_finish(self):
        finish = datetime.today() + timedelta(days=7)
        return fields.Date.context_today(self, timestamp=finish)
    
    def _get_values(self, valeur):
        """
        Return values for the fields 
        """

        val_invoice_file_edi = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.invoice_file_edi')  or ''  
        val_sale_file_edi = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.sale_file_edi')  or ''
        if valeur == 'invoice_file_edi':
            retour = val_invoice_file_edi  
        if valeur == 'sale_file_edi':
            retour = val_sale_file_edi      
                          
        return retour

    date_start = fields.Date('Start Date', help="Starting date", default=lambda self: self._default_start())
    date_end = fields.Date('End Date', help="Ending date", default=lambda self: fields.Date.today())
    invoice_file_edi = fields.Char(string='File For Invoice EDI', default=lambda self: self._get_values('invoice_file_edi'),
                                   help="""The string [datetime] will  be replaced  by the current datetime. It is useful if you want to keep an history of your files and not delete the last one when you make a new one.""")
    sale_file_edi = fields.Char(string='File For Invoice EDI', default=lambda self: self._get_values('sale_file_edi'),
                                help="""The string [datetime] will  be replaced  by the current datetime. It is useful if you want to keep an history of your files and not delete the last one when you make a new one.""")
    edi_select = fields.Char(string='Select EDI')
    re_transfer = fields.Boolean(string="Re-Transfer", default=False)
    edi_data = fields.Binary('EDI File', readonly=True)
    filename = fields.Char(string='Filename', size=256, readonly=True)            
    
    def di_ecrire_ligne_facture(self, invoices_id):
        ligne = ""
        n_fac = invoices_id.name or ''
        date_fac = ""
        heure_fac = ""
        type_doc = 'Facture'
        if invoices_id.move_type == 'out_refund':
            type_doc = 'Avoir'
        code_paiement = 42
        nature_doc = "MAR"
        
        devise = invoices_id.currency_id.name or ""   
        
        n_cde = invoices_id.invoice_origin or ''
        date_cde = ""
        heure_cde = ""
        
        n_liv = invoices_id.invoice_origin or ''  # par défaut si pas de no BL, on prend le no cde
        date_liv = ""
        heure_liv = ""
        
        
        doc_test = "1"
        if invoices_id.partner_id.di_edi_invoice_prod:
            doc_test = "0"
        
        if invoices_id.invoice_origin:
            sale_order_ids = self.env['sale.order'].search([('name' , '=', n_cde)])
            for sale_order_id in sale_order_ids:
                if sale_order_id.date_order:
                    #wdate = sale_order_id.date_order
                    #date_cde = datetime.datetime(wdate.year,wdate.month,wdate.day).strftime("%d/%m/%Y")
                    #heure_cde = datetime.datetime(wdate.hours,wdate.minutes).strftime("%H:%M")
                    date_cde = sale_order_id.date_order.strftime('%d/%m/%Y')
                    heure_cde = sale_order_id.date_order.strftime('%H:%M')
                
                if sale_order_id.effective_date:
                    date_liv = sale_order_id.effective_date.strftime('%d/%m/%Y')
                    
                
                # Livraison 
                bl_ids = self.env['stock.picking'].search([('origin' , '=', n_cde) , ('state' , '=', 'done')])
                for bl_id in bl_ids:
                    n_liv = bl_id.name
                    if bl_id.date_done:
                        date_liv = bl_id.date_done.strftime('%d/%m/%Y')
        
            if date_liv == "":
                    date_liv = date_cde
                    
        if invoices_id.invoice_date:
            date_fac = invoices_id.invoice_date.strftime('%d/%m/%Y')
            
        if invoices_id.invoice_date_due:
            date_ech = invoices_id.invoice_date_due.strftime('%d/%m/%Y')
        
        
        # Segment ENT
        ligne = ""
        ligne = self.di_ligne_fac_ent(invoices_id, ligne, n_cde, date_cde, heure_cde, date_liv, n_liv, n_fac, date_fac, date_ech, type_doc, devise, doc_test, code_paiement, nature_doc)
        
        # Segment DTM : date Bon de livraison
        ligne = self.di_ligne_fac_dtm(invoices_id, ligne, date_liv )
        
            
        # Segment PAR : Partenaire
        #ean_cd_par = invoices_id.partner_id.di_order_code_ean or ""
        #nom_cd_par = invoices_id.partner_id.di_order_name or invoices_id.partner_id.name or ""
        
        ean_cd_par = invoices_id.partner_id.di_code_ean or ""
        nom_cd_par = invoices_id.partner_id.name or ""
        ean_cd_a = invoices_id.company_id.partner_id.di_code_ean or ""
        nom_cd_a = invoices_id.company_id.name or ""
        ean_liv = invoices_id.partner_shipping_id.di_code_ean or ""
        nom_liv = invoices_id.partner_shipping_id.name or ""
        ean_fac = invoices_id.commercial_partner_id.di_code_ean or ""
        nom_fac = invoices_id.commercial_partner_id.name or ""
        ean_regle = invoices_id.commercial_partner_id.di_code_ean or ""
        nom_regle = invoices_id.commercial_partner_id.name or ""
        ean_factor = invoices_id.partner_id.di_code_ean_factor or ""
        nom_factor = invoices_id.partner_id.di_name_factor or ""
        
        ligne = self.di_ligne_fac_par(invoices_id, ligne, ean_cd_par, nom_cd_par, ean_cd_a, nom_cd_a, ean_liv, nom_liv, ean_fac, nom_fac, ean_regle, nom_regle, ean_factor, nom_factor)
        
        
        # Lignes facture
        nb_lig = 0
        #invoices_id.invoice_line_ids = invoices_id.invoice_line_ids.filtered(lambda lig: lig.display_type == False )
        
        if invoices_id.invoice_line_ids:
            for lines in invoices_id.invoice_line_ids.filtered(lambda l: not l.display_type):
                nb_lig+= 1
                code_barre = lines.product_id.barcode or ""
                code_int = lines.product_id.default_code or ""
                qty = lines.quantity or 0
                qty_cde = qty
                unite = "PCE"
                par_combien = 1
                PUN = 0
                if lines.quantity !=0:
                    PUN = abs(lines.balance / lines.quantity)
                PUB = lines.price_unit
                devise = lines.currency_id.name or "" 
                taux_tax = 0
                for tax in lines.tax_ids:
                    code_tax=tax.id  or ""
                    taux_tax = tax.amount or 0
            
                lib=lines.name
                Montant = lines.price_total or 0   
                
                ligne = self.di_ligne_fac_lig(invoices_id, ligne, nb_lig, code_barre, code_int, par_combien, qty_cde, unite, qty, PUN, devise, taux_tax, PUB, lib, Montant)
                
                        
        # Segment PIE : Pied de facture 
        HT = invoices_id.amount_untaxed or 0
        TVA = invoices_id.amount_tax or 0
        TTC = invoices_id.amount_total or 0    
        
        ligne = self.di_ligne_fac_pie(invoices_id, ligne, HT, TVA, TTC )
                        
        # Segment TVA
        if invoices_id.amount_by_group:
            for taxes in invoices_id.amount_by_group:
                M0 = taxes[0]   # Libelle TVA
                M1 = taxes[1]   # Montant TVA
                M2 = taxes[2]   # Montant HT
                Taux = 0.0
                if M2 != 0:
                    Taux = (((M1+M2)*100)/M2)-100 #SC modif calcul taux tva
#                 if M1 != 0:
#                     Taux = M2/M1
                    
                ligne = self.di_ligne_fac_tva(invoices_id, ligne, Taux , M1, M2)
        else:
            # Segment TVA obligatoire même en cas de TVA à 0%
            ligne = self.di_ligne_fac_tva(invoices_id, ligne, 0 , 0, 0 )
                
            
        return ligne.encode("utf-8")

    def di_ligne_fac_ent(self, invoices_id, ligne, n_cde, date_cde, heure_cde, date_liv, n_liv, n_fac, date_fac, date_ech, type_doc, devise, doc_test, code_paiement, nature_doc):
        ligne= "ENT;"
        ligne+= "{};".format(n_cde.replace("\n", " "))
        ligne+= "{};".format(date_cde)
        ligne+= "{};".format(heure_cde)
        ligne+=";;" 
        ligne+= "{};".format(date_liv)
        ligne+= "{};".format(n_liv.replace("\n", " "))
        ligne+=";;;;" 
        ligne+= "{};".format(n_fac.replace("\n", " "))
        ligne+= "{};".format(date_fac)
        ligne+= "{};".format(date_ech)
        ligne+= "{};".format(type_doc)
        ligne+= "{};".format(devise)
        ligne+=";;;;;;;;"
        ligne+= "{};".format(doc_test)
        ligne+= "{};".format(code_paiement)
        ligne+= "{}".format(nature_doc)
        ligne+= "{}".format("\n")
        
        return ligne

    def di_ligne_fac_dtm(self, invoices_id, ligne, date_liv ):
        if date_liv != "":
            ligne+= "DTM;35;"
            ligne+= "{}".format(date_liv)
            ligne+= "{}".format("\n")
        return ligne
    
    def di_ligne_fac_par(self, invoices_id, ligne, ean_cd_par, nom_cd_par, ean_cd_a, nom_cd_a, ean_liv, nom_liv, ean_fac, nom_fac, ean_regle, nom_regle, ean_factor, nom_factor):
        ligne+= "PAR;"
        ligne+= "{};".format(ean_cd_par)
        ligne+= "{};".format(nom_cd_par.replace("\n", " "))    
        ligne+= "{};".format(ean_cd_a)
        ligne+= "{};".format(nom_cd_a.replace("\n", " "))    
        ligne+= "{};".format(ean_liv)
        ligne+= "{};".format(nom_liv.replace("\n", " "))    
        ligne+= "{};".format(ean_fac)
        ligne+= "{};".format(nom_fac.replace("\n", " "))  
        ligne+= "{};".format(ean_factor)
        ligne+= "{};".format(nom_factor.replace("\n", " "))
        ligne+= "{};".format(ean_regle)
        ligne+= "{}".format(nom_regle.replace("\n", " "))  

        ligne+= "{}".format("\n")  
        return ligne

    def di_ligne_fac_lig(self, invoices_id, ligne, nb_lig, code_barre, code_int, par_combien, qty_cde, unite, qty, PUN, devise, taux_tax, PUB, lib, Montant):
        ligne+= "LIG;"
        ligne+= "{};".format(nb_lig)
        ligne+= "{};".format(code_barre)
        ligne+= "{};".format(code_int.replace("\n", " "))
        ligne+="{0:.3f};".format(par_combien)
        ligne+= "{0:.3f};".format(qty_cde)
        ligne+= "{};".format(unite)
        ligne+= "{0:.3f};".format(qty)
        ligne+= "{0:.3f};".format(PUN)
        ligne+= "{};".format(devise)
        ligne+=";;" 
        ligne+= "{0:.2f};".format(taux_tax)
        ligne+= "{0:.3f};".format(PUB)
        ligne+=";"
        ligne+= "{};".format(lib.replace("\n", " "))
        ligne+= "{0:.2f}".format(Montant)
        ligne+= "{}".format("\n")
        return ligne

    def di_ligne_fac_pie(self, invoices_id, ligne, HT, TVA, TTC ):
        ligne+= "PIE;"  
        ligne+= "{0:.2f};".format(HT)      
        ligne+= "{0:.2f};".format(TVA)
        ligne+= "{0:.2f}".format(TTC)
        ligne+= "{}".format("\n")
        return ligne

    def di_ligne_fac_tva(self, invoices_id, ligne, Taux , M1, M2 ):
        ligne+= "TVA;"  
        ligne+= "{0:.1f};".format(Taux)      
        ligne+= "{0:.2f};".format(M2)
        ligne+= "{0:.2f}".format(M1)
        ligne+= "{}".format("\n")
        return ligne

    def di_ecrire_ligne_commande(self, sales_id):
        ligne = ""
        devise = sales_id.currency_id.name    
        date_cde = ""
        heure_cde = ""
        date_liv = ""
        heure_liv = ""
        n_cde = ""
        
        if sales_id.name:
            n_cde = sales_id.name
        
        doc_test = "1"
        if sales_id.partner_id.di_edi_invoice_prod:
            doc_test = "0"
            
        if sales_id.date_order:
            date_cde = sales_id.date_order.strftime('%d/%m/%Y')
            heure_cde = sales_id.date_order.strftime('%H:%M')
        
        if sales_id.effective_date:
            date_liv = sales_id.effective_date.strftime('%d/%m/%Y')
                
        # Livraison 
        bl_ids = self.env['stock.picking'].search([('origin' , '=', n_cde) , ('state' , '=', 'done')])
        for bl_id in bl_ids:
            n_liv = bl_id.name
            if bl_id.date_done:
                date_liv = bl_id.date_done.strftime('%d/%m/%Y')
                heure_liv = bl_id.date_done.strftime('%H:%M')
        
        # Segment ENT
        ligne = self.di_ligne_cde_ent(sales_id, ligne, n_cde, date_cde, heure_cde, devise, date_liv, heure_liv, doc_test)
        
        
        # Segment DTM : date Bon de livraison
        if date_liv != "":
            type_date = 2
            ligne = self.di_ligne_cde_dtm(sales_id, ligne, type_date, date_liv, heure_liv)
            
        # Segment PAR : Partenaire Commandé par
        #ean_cd_par = sales_id.partner_id.di_order_code_ean or ""
        #nom_cd_par = sales_id.partner_id.di_order_name or sales_id.partner_id.name or ""
        ean_cd_par = sales_id.partner_id.di_code_ean or ""
        nom_cd_par = sales_id.partner_id.name or ""
        ref = sales_id.partner_id.ref or ""
        adr1 = sales_id.partner_id.street or ""
        adr2 = sales_id.partner_id.street2 or ""
        zip = sales_id.partner_id.zip or ""
        city = sales_id.partner_id.city or ""
        country = sales_id.partner_id.country_id.code or ""
        adr3=""
        if country!="FR":
            adr3 = sales_id.partner_id.state_id.name or "" 
        
        type_par = "BY"
        ligne = self.di_ligne_cde_par(sales_id, ligne, type_par, ean_cd_par, ref, nom_cd_par, adr1, adr2, adr3, zip, city, country)
        
        
        if sales_id.partner_id.id != sales_id.partner_invoice_id.id:
            # Segment PAR : Partenaire Facturé à
            #ean_fac_a = sales_id.partner_invoice_id.di_order_code_ean or ""
            #nom_fac_a = sales_id.partner_invoice_id.di_order_name or sales_id.partner_id.name or ""
            ean_fac_a = sales_id.partner_invoice_id.di_code_ean or ""
            nom_fac_a = sales_id.partner_invoice_id.name or sales_id.partner_id.name or ""

            ref = sales_id.partner_invoice_id.ref or ""
            adr1 = sales_id.partner_invoice_id.street or ""
            adr2 = sales_id.partner_invoice_id.street2 or ""
            zip = sales_id.partner_invoice_id.zip or ""
            city = sales_id.partner_invoice_id.city or ""
            country = sales_id.partner_invoice_id.country_id.code or ""
            adr3=""
            if country!="FR":
               adr3 = sales_id.partner_invoice_id.state_id.name or "" 
            
            type_par = "IV"
            ligne = self.di_ligne_cde_par(sales_id, ligne, type_par, ean_cd_par, ref, nom_cd_par, adr1, adr2, adr3, zip, city, country)

        # Lignes commande
        nb_lig = 0
        
        if sales_id.order_line:
            for lines in sales_id.order_line.filtered(lambda l: not l.display_type):
                nb_lig+= 1
                code_barre = lines.product_id.barcode or ""
                code_int = lines.product_id.default_code or ""
                qty = lines.product_uom_qty or 0
                unite = "PCE"
                PUN = lines.price_reduce or 0
                PUB = lines.price_unit or 0
                devise = lines.currency_id.name  or ""
                lib=lines.name or ""
                Montant = lines.price_subtotal or 0   
                
                ligne = self.di_ligne_cde_lig(sales_id, ligne, nb_lig, code_barre, code_int, qty, unite, PUN, lib, PUB, PUN, Montant)

                
        return ligne.encode("utf-8")

    def di_ligne_cde_ent(self, sales_id, ligne, n_cde, date_cde, heure_cde, devise, date_liv, heure_liv, doc_test):
        ligne= "ENT;220;"
        ligne+= "{};".format(n_cde.replace("\n", " "))
        ligne+= "{};".format(date_cde)
        ligne+= "{};".format(heure_cde)
        ligne+= "{};".format(devise)
        if date_liv != "": 
            ligne+= "{};".format(date_liv)
            ligne+= "{};".format(heure_liv)
        else:
            ligne+=";;"
            
        ligne+=";;" 
        ligne+= "{};".format(doc_test)
        ligne+= ";"
        ligne+= "{}".format("\n")
        
        return ligne
    
    def di_ligne_cde_dtm(self, sales_id, ligne, type_date, date_liv, heure_liv ):
        ligne+= "DTM;"
        ligne+= "{};".format(type_date)
        ligne+= "{};".format(date_liv)
        ligne+= "{}".format(heure_liv)
        ligne+= "{}".format("\n")        
        return ligne
    
    def di_ligne_cde_par(self, sales_id, ligne, type_par, ean_cd_par, ref, nom_cd_par, adr1, adr2, adr3, zip, city, country):
        ligne+= "PAR;"
        ligne+= "{};".format(type_par)
        ligne+= "{};".format(ean_cd_par)
        ligne+= "{};".format(ref.replace("\n", " "))
        ligne+= "{};".format(nom_cd_par.replace("\n", " "))  
        ligne+= "{};".format(adr1.replace("\n", " "))
        ligne+= "{};".format(adr2.replace("\n", " "))
        ligne+= "{};".format(adr3.replace("\n", " "))
        ligne+= "{};".format(zip.replace("\n", " "))
        ligne+= "{};".format(city.replace("\n", " "))
        ligne+= "{};".format(country)       
        ligne+= ";"
        ligne+= "{}".format("\n")
        
        return ligne

    def di_ligne_cde_lig(self, sales_id, ligne, nb_lig, code_barre, code_int, qty, unite, PUN, lib, PUB, PV, Montant):
        ligne+= "LIG;"
        ligne+= "{};".format(nb_lig)
        ligne+= "{};".format(code_barre)
        ligne+= "{};".format(code_int.replace("\n", " "))
        ligne+=";1;"
        ligne+= "{0:.3f};".format(qty)
        ligne+= "{};".format(unite)
        ligne+= "{0:.3f};".format(PUN)
        ligne+= "{};".format(lib.replace("\n", " "))
        ligne+=";;;;;;;;;"
        ligne+= "{0:.3f};".format(PUB)
        ligne+= "{0:.3f};".format(PV)
        ligne+=";;;"
        ligne+= "{0:.2f}".format(Montant)
        ligne+=";;;;"
                
        ligne+= "{}".format("\n")
        return ligne
    
        
    def di_ecrire_ligne_Fin(self):
        ligne= "END"
        ligne+= "{}".format("\n")
        return ligne.encode("utf-8")
    
    def edi_invoice(self, **kw):  
        nb_fac = 0
        
        #wdate = self.date_start 
        #date_d = datetime.datetime(wdate.year,wdate.month,wdate.day,0,0,0,0).strftime("%Y-%m-%d %H:%M:%S")
        #wdate = self.date_end
        #date_f = datetime.datetime(wdate.year,wdate.month,wdate.day,23,59,59,0).strftime("%Y-%m-%d %H:%M:%S")
        
        date_d=self.date_start.strftime('%Y%m%d')
        wdate = self.date_end + relativedelta(days=1)
        date_f = wdate.strftime('%Y%m%d')

        
        #_invoices_ids = self.env['account.move'].search([('date','>=',date_d),('date','<=',date_f), ('state', '=' ,'posted'), ('move_type', 'in' ,['out_invoice','out_refund']) ])
        if self.re_transfer:
            #invoices_ids = _invoices_ids.filtered(lambda inv: inv.di_transfer_edi == True )
            invoices_ids = self.env['account.move'].search([('date','>=',date_d),('date','<=',date_f), ('state', '=' ,'posted'), ('move_type', 'in' ,['out_invoice','out_refund']), ('invoice_origin' ,'!=' , False), ('partner_id.di_edi_invoice' ,'=' , True), ('di_transfer_edi' ,'=' , True) ])
        else:
            #invoices_ids = _invoices_ids.filtered(lambda inv: inv.di_transfer_edi == False )
            invoices_ids = self.env['account.move'].search([('date','>=',date_d),('date','<=',date_f), ('state', '=' ,'posted'), ('move_type', 'in' ,['out_invoice','out_refund']), ('invoice_origin' ,'!=' , False), ('partner_id.di_edi_invoice' ,'=' , True), ('di_transfer_edi' ,'=' , False) ])    
        
        if invoices_ids:
            edi_file = self.invoice_file_edi
            if edi_file is None:    
                edi_file = 'factures_edi.txt'
            
            edi_file = edi_file.replace('[datetime]',datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            
            invoice_file = io.BytesIO()    
        
            for invoices_id in invoices_ids:
                if invoices_id.invoice_origin != "" and invoices_id.invoice_origin.rfind(',') == -1 :   # La facture doit venir d'une seule commande
                    listrow = self.di_ecrire_ligne_facture(invoices_id)
                    invoice_file.write(listrow)
                    nb_fac +=1
                
                    #flag des factures exportées  
                    invoices_id.update({
                            'di_transfer_edi': True,
                        })
       
        
        if nb_fac == 0:
            raise ValidationError(_('No selected invoice' ))
            return {'type': 'ir.actions.act_window_close'} 
        else: 
            # Ecriture dernier segment
            listrow = self.di_ecrire_ligne_Fin()
            invoice_file.write(listrow)
  
            # Téléchargement du fichier
            invoicevalue = invoice_file.getvalue()
            
            self.write({
#                     'edi_data': base64.encodestring(invoicevalue),
                    'edi_data': base64.encodebytes(invoicevalue),     #SC encodestring est dépréciée   
                    'filename': edi_file,
                })
            
            
            """
            from ftplib import FTP
            from io import BytesIO
            import csv

            flo = BytesIO() 
            writer = csv.writer(flo, delimiter=';')
            writer.writerow(...)

            ftp = FTP('ftp.groupeadinfo.info')
            ftp.login('be', '@be_FTP')
            flo.seek(0)
            ftp.storbinary('STOR test.csv', flo)
            
            """
  
  
            """
            IP = "xx.xx.xx.xx"
            path_file1 = "./MyFile1.py"
            path_file2 = "./MyFile2.py"
            UID = ""
            PSW = ""

            ftp = ftplib.FTP(IP)
            ftp.login(UID, PSW)
            ftp.cwd("/Unix/Folder/where/I/want/to/put/file")

            with open(path_file1, 'r') as myfile: ftp.storlines('STOR ' + filename, myfile)
            with open(path_file2, 'r') as myfile: ftp.storlines('STOR ' + filename, myfile)
            
            """
            try:
                ftp_address = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_address')  or ''  
                ftp_login = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_login')  or ''
                ftp_password = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_password')  or ''
                ftp_directory = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_directory')  or ''
            
                #ftp = FTP('ftp.groupeadinfo.info')
                #ftp.login('be', '@be_FTP')
                ftp = FTP(ftp_address)
                ftp.login(ftp_login, ftp_password)
                if ftp_directory:
                    if not self.directory_exists_ftp(ftp, ftp_directory):
                        ftp.mkd('/' + ftp_directory)
                    ftp.cwd('/' + ftp_directory)
                
                invoice_file.seek(0)
                
                ftp.storbinary('STOR ' + edi_file, invoice_file)
                ftp.quit()  
                
                _message = _('Export file invoice by FTP : OK.' + '\n' + 'Do you want to export the EDI file on your local disk ?')
                 
            except Exception as e:
                _message = _('Export file invoice by FTP : Error : "%s". ' + '\n' + 'Do you want to export the EDI file on your local disk ?' ) % (e,)
                
            invoice_file.close()
            
            """          
            action = {
                    'name': 'miadi_invoice_edi',
                    'type': 'ir.actions.act_url',
                    'url': "web/content/?model=wiz.edi.ftp&id=" + str(self.id) + "&filename_field=filename&field=edi_data&download=true&filename=" + self.filename,
                    'target': 'self',
                    
                    }
            return action 
            """
            
            
            return self.env['wiz.dialog'].show_dialog(_message,"file-invoice",self.id, self.filename )
            
    def edi_sale(self, **kw):  
        nb_cde = 0
        
        date_d=self.date_start.strftime('%Y%m%d')
        wdate = self.date_end + relativedelta(days=1)
        date_f = wdate.strftime('%Y%m%d')

        if self.re_transfer:
            sales_ids = self.env['sale.order'].search([('date_order','>=',date_d),('date_order','<=',date_f), ('invoice_status', '=' ,'to invoice'), ('di_transfer_edi' ,'=' , True) ])
        else:
            sales_ids = self.env['sale.order'].search([('date_order','>=',date_d),('date_order','<=',date_f), ('invoice_status', '=' ,'to invoice'), ('di_transfer_edi' ,'=' , False) ])    
        
        if sales_ids:
            edi_file = self.sale_file_edi
            if edi_file is None:    
                edi_file = 'commandes_edi.txt'
                
            edi_file = edi_file.replace('[datetime]',datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            
            sale_file = io.BytesIO()    
        
            for sales_id in sales_ids:
                listrow = self.di_ecrire_ligne_commande(sales_id)
                sale_file.write(listrow)
                nb_cde +=1
                
                #flag des commandes exportées  
                sales_id.update({
                            'di_transfer_edi': True,
                        })
       
        
        if nb_cde == 0:
            raise ValidationError(_('No selected sale' ))
            return {'type': 'ir.actions.act_window_close'} 
        else: 
            # Ecriture dernier segment
            listrow = self.di_ecrire_ligne_Fin()
            sale_file.write(listrow)
  
            # Téléchargement du fichier
            salevalue = sale_file.getvalue()
            
            self.write({
#                     'edi_data': base64.encodestring(salevalue),  
                    'edi_data': base64.encodebytes(salevalue),      #SC encodestring est dépréciée     
                    'filename': edi_file,
                })
            
            try:
                ftp_address = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_address')  or ''  
                ftp_login = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_login')  or ''
                ftp_password = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_password')  or ''
                ftp_directory = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_directory')  or ''
            
                ftp = FTP(ftp_address)
                ftp.login(ftp_login, ftp_password)
                if ftp_directory:
                    if not self.directory_exists_ftp(ftp, ftp_directory):
                        ftp.mkd('/' + ftp_directory)
                    ftp.cwd('/' + ftp_directory)
                
                sale_file.seek(0)
                ftp.storbinary('STOR ' + edi_file, sale_file)
                ftp.quit()  
                
                _message = _('Export file sale by FTP : OK.' + '\n' + 'Do you want to export the EDI file on your local disk ?')
                 
            except Exception as e:
                _message = _('Export file sale by FTP : Error : "%s". ' + '\n' + 'Do you want to export the EDI file on your local disk ?' ) % (e,)
                
            
            sale_file.close()
            
            return self.env['wiz.dialog'].show_dialog(_message,"file-sale",self.id, self.filename )
            
 
 
    def directory_exists_ftp(self, ftp, directory_name):
        filelist = []
        ftp.retrlines('LIST',filelist.append)
        for f in filelist:
            if f.split()[-1] == directory_name:
                return True
        return False
    
    def edi_sale_import(self, **kw): 
        _message = ""
        ids = []
        try:
            ftp_address = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_address')  or ''  
            ftp_login = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_login')  or ''
            ftp_password = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_password')  or ''
            
            ftp_directory = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_directory_import_sale')  or ''
            ftp_search_file = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_sale_file')  or '*.txt'
            
            local_repert = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.local_directory_import_sale')
            if local_repert is False or local_repert is None:
                local_repert = os.environ.get('LOCALAPPDATA') or os.getcwd()    
            local_repert = os.path.normpath(local_repert)
            if not local_repert.endswith('\\'):
                local_repert = local_repert + '\\' 
        
            if not os.path.exists(local_repert):
               os.mkdir(local_repert)
 

            ftp = FTP(ftp_address)
            ftp.login(ftp_login, ftp_password)
            if ftp_directory:
                ftp.cwd('/' + ftp_directory)
               
            try:
                filelist = ftp.nlst(ftp_search_file)
            except ftplib.error_perm as x:
                if (x.args[0][:3] != '550'):
                    raise
                else:
                    _message = _('No file sale to import' + '\n' + '')
                            
            if (_message == ""):
                nbr = 0
                for hostfile in filelist:
                    lines = []
                    ftp.retrlines("RETR "+hostfile, lines.append)
                    
                    # Traitement de la ligne pour création Sale_order
                    ids = self.di_import_cde(lines, ids)
                                                   
                    nbr += 1
                    #nomfile = local_repert + time.strftime("%Y%m%d_%H%M%S_") + hostfile
                    nomfile = local_repert + hostfile
                    with open(nomfile, "w") as pcfile:
                        for line in lines:
                            #line = line.replace("\n\t", "")
                            #    regex = re.compile(r'[\n\r\t]')
                            #    line = regex.sub("", line)
                            
                            if (line != ""):
                                # Ecriture de la ligne dans un fichier texte
                                pcfile.write(line.rstrip('\r\n') + "\n")
                             
                        pcfile.close()
            
                    # Renomme le fichier dans FTP
                    #newname = hostfile + time.strftime("_%Y%m%d_%H%M%S") + ".old"
                    newname = hostfile + ".old"
                    #ftp.rename(hostfile, newname)
                    # Supprime le fichier dans FTP
                    ftp.delete(hostfile)
                    
                    
                _message = _('Import "%s" file sale by FTP : OK.' + '\n')  % (nbr,)
                

                    #with open(hostfile, "wb") as file:
                    #    ftp.retrbinary(f"RETR {hostfile}", file.write)
                
            ftp.quit()  
                
                 
        except Exception as e:
            _message = _('Export file sale by FTP : Error : "%s". ' + '\n'  ) % (e,)
            if (nbr !=0):
                _message += _('Import "%s" file sale by FTP : OK.' + '\n')  % (nbr,)

        if ((ids) and (_message.find('Error') <= 0) and (_message.find('Erreur') <= 0)):                
            action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations")  
            action['domain'] = [('id', 'in', ids)]
            return action
        else:
            return self.env['wiz.dialog'].show_dialog(_message,"",self.id, "" )
        
            
    def di_import_cde(self, lines, ids):
        creation_cde = False
        creation_lig = False
        #ref_sale_vals = None
                
        for line in lines:
            if (line != ""):
                line_cde = []
                line_cde = line.split(";")
                drapeau = line_cde[0]
                if (drapeau == "ENT"):
                    if creation_cde:
                        edi_sales_order = self.di_import_entete(Numero, Date_Cde, Date_Liv, code_devise, line_par_by, line_par_dp)
                        if (edi_sales_order):
                            ids.append(edi_sales_order.id)
                        line_par_by = ""
                        line_par_dp = ""
                    
                    if creation_lig:
                        edi_sales_lines = self.di_import_line(edi_sales_order, ean_lig, par_combien, qte_cde, unite_cde )
                        
                    creation_lig = False
                
                    #ENT;220;00002793978;20/11/2019;00:00;EUR;22/11/2019;00:00;;;0;;    
                    Numero =  line_cde[2]
                    Date_Cde =  line_cde[3]
                    Date_Liv =  line_cde[6]
                    code_devise =  line_cde[5]
                    creation_cde = True;
                
                if (drapeau == "PAR"):  
                    type_par = line_cde[1]
                    if (type_par == "BY"):
                        line_par_by = line
                        #PAR;BY;3020114963203;CE632;ENTREPOT CHOLET;PETITES SURFACES FRAIS ET MAREE;BOULEVARD DU POITOU;;49300;CHOLET;FR;;
                    
                 
                    if (type_par == "DP"):
                        #PAR;DP;3020114963203;CE632;ENTREPOT CHOLET;PETITES SURFACES FRAIS ET MAREE;BOULEVARD DU POITOU;;49300;CHOLET;FR;;
                        line_par_dp = line
                    
            
                if (drapeau == "LIG"):
                    if creation_lig:
                        if creation_cde:
                            edi_sales_order = self.di_import_entete(Numero, Date_Cde, Date_Liv, code_devise, line_par_by, line_par_dp)
                            if (edi_sales_order):
                                ids.append(edi_sales_order.id)
                            
                        edi_sales_lines = self.di_import_line(edi_sales_order, ean_lig, par_combien, qte_cde, unite_cde )
                        creation_cde = False
                        
                        
                    #LIG;1;3375160000847;;;12;72.000;PCE;0.000000;;;;;;;;;;;0.000000;;;;;;;;;
                    no_lig = line_cde[1]
                    ean_lig = line_cde[2]
                    par_combien = line_cde[5]
                    qte_cde = line_cde[6]
                    unite_cde  = line_cde[7]
                    creation_lig = True
                    
                
                if (drapeau == "PAC"):
                    #PAC;pc;6;23375160000841
                    type_colis = line_cde[1]
                    ean_colis = line_cde[2]
                    qte_colis = line_cde[3]
                    
        # Fin des lignes : on gére les dernières création
        if creation_cde:
            edi_sales_order = self.di_import_entete(Numero, Date_Cde, Date_Liv, code_devise, line_par_by, line_par_dp)
            if (edi_sales_order):
                ids.append(edi_sales_order.id)
                    
        if creation_lig:
            edi_sales_lines = self.di_import_line(edi_sales_order, ean_lig, par_combien, qte_cde, unite_cde )
        
        return ids
        
    def di_import_entete(self, Numero, Date_Cde, Date_Liv, code_devise, line_par_by, line_par_dp):
        edi_sales_order = None
        if (line_par_by):
            line_par = line_par_by.split(";")
            ean_par = line_par[2]
            interne_par = line_par[3]
            rs_par = line_par[4]
            ad1_par = line_par[5]
            ad2_par = line_par[6]
            ad3_par = line_par[7]
            cp_par = line_par[8]
            ville_par = line_par[9]
            pays_par = line_par[10]
        
        if (line_par_dp):
            line_par = line_par_dp.split(";")
            ean_liv = line_par[2]
            interne_liv = line_par[3]
            rs_liv = line_par[4]
            ad1_liv = line_par[5]
            ad2_liv = line_par[6]
            ad3_liv = line_par[7]
            cp_liv = line_par[8]
            ville_liv = line_par[9]
            pays_liv = line_par[10]
          
        # Search partner
        partner_cde = self.env['res.partner'].search(
            [('di_code_ean', '=', ean_par)], limit=1)  
        
        if (ean_liv):
            partner_liv = self.env['res.partner'].search(
                [('di_code_ean', '=', ean_liv)], limit=1)
        
        if (partner_cde): 
            vals = {}
            vals['partner_id'] = partner_cde.id
            if (partner_liv):
                vals['partner_shipping_id'] = partner_liv.id
            vals['date_order'] =  Date_Cde[6:10] + "-" + Date_Cde[3:5] + "-" + Date_Cde[0:2]
            if (Date_Liv):
                vals['commitment_date'] =  Date_Liv[6:10] + "-" + Date_Liv[3:5] + "-" + Date_Liv[0:2]
            
            edi_sales_order = self.env['sale.order'].create(vals)
        else:
            raise ValidationError(
                    _("The partner's bar code  '%s' does not exist ") % (ean_par)    
                    )
        return edi_sales_order
    
    def di_import_line(self, edi_sales_order, ean_lig, par_combien, qte_cde, unite_cde):    
        if (edi_sales_order):
            # Search product
            product = self.env['product.template'].search(
                [('barcode', '=', ean_lig)], limit=1)  
            if (product) :
                self.env['sale.order.line'].create({
                    'product_id': product.id,
                    'product_uom_qty': qte_cde,
                    'order_id': edi_sales_order.id,
                    'company_id': edi_sales_order.company_id.id,
                    })
            else:
                self.env['sale.order.line'].create({
                    'display_type': 'line_note',
                    'name': 'Unknown bar code ' + ean_lig + ' quantity = ' + str(qte_cde),
                    'product_id': False,
                    'product_uom_qty': False,
                    
                    'order_id': edi_sales_order.id,
                    'company_id': edi_sales_order.company_id.id,
                    })
            
            
            