# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import os, sys

#from ..controllers import ctrl_print

class wizard_printetiquette(models.TransientModel):
    _name = "wiz_print_etiquette"
    _description = "Wizard print etiquette"
    
    printer_id = fields.Many2one("di.printing.printer", required=True)
    etiquette_id = fields.Many2one("di.printing.etiqmodel", required=True)
    #message = fields.Text(string="Information")

    def print_etiquette(self):
        printerName = self.printer_id.name
        etiquetteFile = self.etiquette_id.text_etiq 
        
        test = [("key1","value1"),("key2","value2"),("key3","value3"),("saleline_qty",1)]
        
        #ctrl_print.printetiquetteonwindows(self, printerName,etiquetteFile,'[',test)
        #ctrl_print.PrintingLabel.printetiquetteonwindows(self, printerName,etiquetteFile,'[',test)
        self.env['di.printing.printing'].printetiquetteonwindows( printerName,etiquetteFile,'[',test)
        return {'type': 'ir.actions.act_window_close'}  
 