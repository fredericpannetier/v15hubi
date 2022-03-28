# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import os, sys

class MIADI_EtiquetteImpression(models.Model):
    _name = "di.printing.printing"
    _description = "Printing"
    #_order = "name"
    
    printer_name = fields.Char(string="Printer name", required=True)
    etiquette_text = fields.Text(string="Text of label to print", required=True)
    count = fields.Integer(string="Number of etiqettes to print", required=True,default=1)
    printed = fields.Boolean(string="Is printed ?",default=False)
    printing_date = fields.Datetime(string="Printing date", required=False)
    order_line = fields.Many2one('sale.order.line', string="Linked order line", help="Linked to an order line", required=False)
    order_name = fields.Char(string="Linked order", required=False)
    real_number_etiq = fields.Integer(string="Real number of etiquettes to print", required=False,default=0)
    
    def replace_accent_zpl(self,s):
        if s:
            s = s.replace('ê', '\\88') \
                 .replace('è', '\\8a') \
                 .replace('é', '\\82') \
                 .replace('à', '\\85') \
                 .replace('â', '\\83') \
                 .replace('á', '\\a0') \
                 .replace('ô', '\\93') \
                 .replace('ö', '\\94') \
                 .replace('î', '\\8c') \
                 .replace('É', '\\90') \
                 .replace('È', '\\d4') \
                 .replace('Ê', '\\d2') \
                 .replace('À', '\\b7') \
                 .replace('Â', '\\b6') \
                 .replace('Á', '\\b5') \
                 .replace('Ô', '\\e2') \
                 .replace('Ö', '\\94') \
                 .replace('Î', '\\d7')
        return s

    def printetiquetteonwindows(self, printer, etiqtext, charSepBegin, charSepEnd, langage_print, parameters, number_etiquette = 0):
        contenu = etiqtext 
        sale_ordername = ''
        saleline_id = 0
    
        for paramName, value in parameters:
            if paramName == 'sale_ordername':
                sale_ordername = value
            if paramName == "saleline_id":
                saleline_id = value
            if paramName == "saleline_qty":
                number_etiquette = value            
            if contenu.find(charSepBegin + paramName.lower() + charSepEnd) != -1:
                if (value is not None):
                    contenu = contenu.replace(charSepBegin + paramName.lower() + charSepEnd, str(value))
                else:
                    contenu = contenu.replace(charSepBegin + paramName.lower() + charSepEnd, "")
        
        while contenu.find("[IF") != -1:
            start_if = contenu.find("[IF")
            end_if = contenu.find("]", start_if)
            entire_if = contenu[start_if:end_if]
            part_if = entire_f[1:-2].split(";")
            if part_if[1] == part_if[2]:
                contenu = contenu.replace(entire_if, part_if[3])
            else:
                contenu = contenu.replace(entire_if, part_if[4])
            
        if langage_print = "ZPL":
            contenu = replace_accent_zpl(contenu)
        
        if sys.version_info >= (3,):
            raw_data = bytes(contenu, "utf-8")
        else:
            raw_data = contenu

        printing_vals = {
        'printer_name': printer,
        'etiquette_text': contenu,
        'count': 1,
        'printed': False,
        'order_line': saleline_id,
        'order_name': sale_ordername,
        'real_number_etiq': number_etiquette,
        }
        self.env['di.printing.printing'].create(printing_vals)
    