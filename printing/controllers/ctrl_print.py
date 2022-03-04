# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from . import models,wizards
import os, sys

# import win32print
# from odoo.http import request
# from unidecode import unidecode

class PrintingLabel(object):
    def printetiquetteonwindows(self, printer, etiqtext, charSep, parameters):
        contenu = etiqtext  # "";
        sale_ordername = ''
        saleline_id = 0
        number_etiquette = 0
    
        for paramName, value in parameters:
            if paramName == 'sale_ordername':
                sale_ordername = value
            if paramName == "saleline_id":
                saleline_id = value
            if paramName == "saleline_qty":
                number_etiquette = value
            if contenu.find(charSep + paramName.lower() + charSep) != -1:
                if (value is not None):
                    contenu = contenu.replace(charSep + paramName.lower() + charSep,
                                          str(value).replace("é", "\\82").replace("à", "\\85").replace("î", "\\8C"))
                else:
                    contenu = contenu.replace(charSep + paramName.lower() + charSep, "")

        if sys.version_info >= (3,):
            raw_data = bytes(contenu, "utf-8")
        else:
            raw_data = contenu

        printing_vals = {
        'di_printer_name': printer,
        'di_etiquette_text': contenu,
        'di_count': 1,
        'di_printed': False,
        'di_order_line': saleline_id,
        'di_order_name': sale_ordername,
        'di_real_number_etiq': number_etiquette,
        }
        self.env['di.printing.printing'].create(printing_vals)


    def callFonction(self):
        return
