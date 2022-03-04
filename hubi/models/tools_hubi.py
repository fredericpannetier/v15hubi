# -*- coding: utf-8 -*-

from odoo import models, fields, api

"""                    
def calcul_cle_code_ean13(self, ean):
    # Calcul cle code ean13
    somme = 0
    coeff = "131313131313"

    for i in range(0,12):
        somme = somme + int(ean[i])*int(coeff[i])

    reste = somme % 10
    if reste == 0:
        cle = 0
    else: 
        cle = 10 - reste
        
    return "%s" % (cle) 

def replace_accent(self,s):
    if s:
        s = s.replace('ê', 'e') \
             .replace('è', 'e') \
             .replace('é', 'e') \
             .replace('à', 'a') \
             .replace('â', 'a') \
             .replace('á', 'a') \
             .replace('ô', 'o') \
             .replace('ö', 'o') \
             .replace('î', 'i') \
             .replace('É', 'E') \
             .replace('È', 'E') \
             .replace('Ê', 'E') \
             .replace('À', 'A') \
             .replace('Â', 'A') \
             .replace('Á', 'A') \
             .replace('Ô', 'O') \
             .replace('Ö', 'O') \
             .replace('Î', 'I')
    return s                 
                      
def left(aString, howMany):
    if howMany <1:
        return ''
    else:
        return aString[:howMany]

def right(aString, howMany):
    if howMany <1:
        return ''
    else:
        return aString[-howMany:]

def mid(aString, startChar, howMany):
    if howMany < 1:
        return ''
    else:
        return aString[startChar:startChar+howMany]
"""

#@api.model
def prepareprintetiq(self, nom_table, id_table):
        #FP20190318 Remplacement l.file par l.text et sl.pds par case ...sl.pds / sl.qte end
        query = """SELECT to_char(sl.packaging_date,'DD/MM/YYYY'), to_char(sl.sending_date,'DD/MM/YYYY'), 
                    pt.di_etiq_description, pc.complete_name, 
                    hfc.name, hfp.name, pt.di_etiq_mention, 
                    sl.code_barre, sl.code_128, sl.qte,  
                    case sl.qte when 0 then sl.pds else sl.pds/sl.qte end,
                    sl.nb_mini, p.realname, p.adressip, l.text_etiq,
                    t.di_customer_name_etiq, t.di_customer_city_etiq, 
                    etab.di_health_number, etab.di_company_name_etiq, etab.di_company_city_etiq, etab.di_etiq_mention,
                    sl.numlot, sl.color_etiq, pt.di_etiq_latin, pt.di_etiq_spanish, pt.name, 
                    l.with_ean128, etab.di_compteur_ean128, etab.id, dc.name,
                    t.di_statistics_alpha_1, t.di_statistics_alpha_2,t.di_statistics_alpha_3,t.di_statistics_alpha_4,t.di_statistics_alpha_5,
                    pt.di_statistics_alpha_1, pt.di_statistics_alpha_2,pt.di_statistics_alpha_3,pt.di_statistics_alpha_4,pt.di_statistics_alpha_5,
                    pt.di_etiq_english, pt.di_etiq_italian,pt.di_etiq_portuguese, sl.date_dluo, """
        if (nom_table == 'wiz_sale_order_print_etiq'):
            query += """sale_order_num as saleorder, sale_order_line_id::INTEGER as saleorderline """
        else:
            query += """'' as saleorder, 0 as saleorderline """
        query += """FROM """ + nom_table + """ sl
                    LEFT JOIN di_printing_printer p ON sl.printer_id = p.id 
                    LEFT JOIN di_printing_etiqmodel l ON sl.model_id = l.id
                    INNER JOIN res_partner t ON t.id = sl.partner_id
                    LEFT JOIN res_partner etab ON etab.id = sl.etabexp_id
                    INNER JOIN product_product prod ON prod.id = sl.product_id
                    INNER JOIN product_template pt ON prod.product_tmpl_id = pt.id
                    INNER JOIN product_category pc ON pt.categ_id = pc.id 
                    LEFT JOIN di_multi_table AS hfc ON pt.di_caliber_id = hfc.id 
                    LEFT JOIN di_multi_table AS hfp ON pt.di_packaging_id = hfp.id 
                    LEFT JOIN delivery_carrier as dc on sl.carrier_id = dc.id 

                    WHERE sl.id=""" + str(id_table)
                    #t.statistics_num_1, t.statistics_num_2,t.statistics_num_3,t.statistics_num_4,t.statistics_num_5,
                    #pt.statistics_num_1, pt.statistics_num_2,pt.statistics_num_3,pt.statistics_num_4,pt.statistics_num_5

        self.env.cr.execute(query)
        
        result = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], \
                    r[11], r[12], r[13], r[14], r[15], r[16], r[17], r[18], r[19], r[20], \
                    r[21], r[22], r[23], r[24], r[25], r[26], r[27], r[28], r[29], r[30], \
                    r[31], r[32], r[33], r[34], r[35], r[36], r[37], r[38], r[39], r[40], \
                    r[41], r[42], r[43], r[44], r[45]) \
                  for r in self.env.cr.fetchall()]
        
        for packaging_date,sending_date,product_description,category_name,caliber_name,packaging_name,etiq_mention,code_barre,code128,qte, pds, \
        nb_mini,printerName,adressip,labelFile,clientname1,clientname2,numsanitaire,etabexp1,etabexp2,etab_mention,\
        lot,color,etiq_latin, etiq_spanish,product_name,with_ean128,compteur_ean128, etab_id, carrier_name, c_st1, \
        c_st2, c_st3, c_st4, c_st5, p_st1, p_st2, p_st3, p_st4, p_st5, etiq_english, etiq_italian, etiq_portuguese, \
        date_dluo, saleorder, saleorderline in result:
            if (product_description is not None):
                description_item = product_description
            else:
                description_item = category_name  
                
            if (etiq_mention is not None):
                mention_item = etiq_mention
            else:
                mention_item = etab_mention  
                
            informations = [
                ("dateemb",packaging_date),
                ("dateexp",sending_date),
                ("produit",description_item),
                ("calibre",caliber_name),
                ("conditionnement",packaging_name),
                ("mention",mention_item),
                ("latin",etiq_latin),
                ("spanish",etiq_spanish),
                ("codebarre",code_barre),
                ("codeb128",code128),
                ("qte",int(qte)),
                ("pds",pds),
                ("nb",int(nb_mini)),
                ("numsanitaire",numsanitaire),
                ("client1", clientname1),
                ("client2", clientname2),
                ("etab1", etabexp1),
                ("etab2", etabexp2),
                ("lot", lot),
                ("color", color),
                ("date_dlc", date_dluo),
                
                ("sale_ordername",saleorder),
                ("sale_packaging_date",packaging_date),
                ("sale_sending_date",sending_date),
                ("saleline_id",int(saleorderline)),
                ("saleline_qty",int(qte)),
                ("saleline_weight",pds),
                ("saleline_no_lot", lot),
                
                ("product_produit",description_item),
                ("product_caliber_name",caliber_name),
                ("product_packaging_name",packaging_name),
                ("product_etiq_mention",mention_item),
                ("product_etiq_latin",etiq_latin),
                ("product_etiq_spanish",etiq_spanish),
                ("product_etiq_english",etiq_english),
                ("product_etiq_italian",etiq_italian),
                ("product_etiq_portuguese",etiq_portuguese),
                ("product_barcode",code_barre),
                ("product_barcode128",code128),
                ("product_nbmini",int(nb_mini)),
                ("product_stat1", p_st1),
                ("product_stat2", p_st2),
                ("product_stat3", p_st3),
                ("product_stat4", p_st4),
                ("product_stat5", p_st5),
                
                ("customer_etiq_name", clientname1),
                ("customer_etiq_city", clientname2),
                ("customer_carrier_name", carrier_name),
                ("customer_stat1", c_st1),
                ("customer_stat2", c_st2),
                ("customer_stat3", c_st3),
                ("customer_stat4", c_st4),
                ("customer_stat5", c_st5),
                
                ("etab_health_number",numsanitaire),
                ("etab_etiq_name", etabexp1),
                ("etab_etiq_city", etabexp2),
                ]
            
            if(printerName is not None and printerName != "" and labelFile is not None and labelFile != ""):
                printer = printerName
                #FP20190318 if (adressip is not None and adressip != ""):
                #    printer = "\\\\" + adressip + "\\" + printerName
                #else:
                #    printer = printerName
                    
                #ctrl_print.PrintingLabel.printetiquetteonwindows(self,printer,labelFile,'[',informations)   
                self.env['di.printing.printing'].printetiquetteonwindows(printer,labelFile,'[',informations)
                
                # Update counter of barcode 128
                if with_ean128:
                    if compteur_ean128:
                        compteur_ean128 += 1
                    else:
                        compteur_ean128 = 2    
                    req = """UPDATE res_partner SET di_compteur_ean128=%s  where id=%s"""
        
                    params = (compteur_ean128, etab_id)
                    self._cr.execute(req,params)
                    self.env.cr.commit()


def prepareprintetiqcarrier(self, nom_table, id_table):
        if id_table:
            printerName =""
            labelFile =""
            
            _etiq_pallet_printer_id = self.env['ir.config_parameter'].sudo().get_param('hubi.di_etiq_pallet_printer_id')
            if _etiq_pallet_printer_id:
                _pallet_printer = self.env['di.printing.printer'].browse(_etiq_pallet_printer_id).exists()
                pallet_printer = self.env['di.printing.printer'].search([('id', '=', _etiq_pallet_printer_id), ]) 
                for printer in  pallet_printer:
                    printerName = printer.realname

            
            _etiq_pallet_model_id = self.env['ir.config_parameter'].sudo().get_param('hubi.di_etiq_pallet_model_id')
            if _etiq_pallet_model_id:
                _pallet_model = self.env['di.printing.etiqmodel'].browse(_etiq_pallet_model_id).exists()
                pallet_model = self.env['di.printing.etiqmodel'].search([('id', '=', _etiq_pallet_model_id), ]) 
                for pallet in pallet_model:
                    labelFile = pallet.text_etiq
                
            saleorder = self.env['sale.order'].search([('id', '=', id_table), ])         
            for sale in saleorder:
                client_name1 = sale.partner_id.di_customer_name_etiq or sale.partner_id.name
                client_name2 = sale.partner_id.di_customer_city_etiq or sale.partner_id.state_id.name
                carrier_name = sale.carrier_id.name
                etab_exp1 = sale.partner_id.di_sender_establishment.di_company_name_etiq or ""
                etab_exp2 = sale.partner_id.di_sender_establishment.di_company_city_etiq or ""
                sending_date = ""
                packaging_date = ""
                commitment_date = ""
                if sending_date:
                    sending_date = fields.Date.from_string(sale.di_sending_date).strftime('%d/%m/%Y')
                if packaging_date:    
                    packaging_date = fields.Date.from_string(sale.di_packaging_date).strftime('%d/%m/%Y')
                if commitment_date:
                    commitment_date = fields.Date.from_string(sale.commitment_date).strftime('%d/%m/%Y')
                
                ordername = sale.name
                code_barre = ""
                
                # Lecture des lignes Palettes : 1 étiquette par palette
                num_pallet = "999"
                linepallet = self.env['hubi.palletization.line'].search([
                    ('order_id', '=', sale.id)
                    
                     ]) 
                
                description_item = ""
                pallet_qty = 0        
                for line in linepallet:
                    if num_pallet != line.pallet_no and num_pallet != "999":
                        # impression
                        if(printerName is not None and printerName != "" and labelFile is not None and labelFile != ""):
                            self.env['di.printing.printing'].printetiquetteonwindows(printerName,labelFile,'[',informations)
                        num_pallet = ""
                        description_item = ""
                        pallet_qty = 0
                            
                    num_pallet = line.pallet_no
                    description_item += line.product_id.pallet_description or line.product_id.name + " "
                    pallet_qty += line.quantity
                    package = str(pallet_qty)+ " colis"
                
                    informations = [
                                ("dateemb",packaging_date),
                                ("dateexp",commitment_date),
                                ("dateenvoi",sending_date),
                                ("produit",description_item),
                                ("codebarre",code_barre),
                                
                                ("package",int(pallet_qty)),
                                ("client1", client_name1),
                                ("client2", client_name2),
                                ("etab1", etab_exp1),
                                ("etab2", etab_exp2),
                
                                ("ordername",ordername),
                                
                                ("customer_etiq_name", client_name1),
                                ("customer_etiq_city", client_name2),
                                ("customer_carrier_name", carrier_name),
                
                                ("etab_etiq_name", etab_exp1),
                                ("etab_etiq_city", etab_exp2),
                                ]
            
        
                if num_pallet != "" and num_pallet != "999":
                        # impression de la dernière étiquette
                        if(printerName is not None and printerName != "" and labelFile is not None and labelFile != ""):
                            self.env['di.printing.printing'].printetiquetteonwindows(printerName,labelFile,'[',informations)
          
                #title = ("Etiquette for %s") % ordername
                #message = 'Etiquette - ' + printerName + ' OK '
                #warning = {
                #    'title': title,
                #    'message': message, }
                #return {'warning': warning}  