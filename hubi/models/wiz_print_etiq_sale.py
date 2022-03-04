from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import os, sys
#import win32print
#from ..controllers import ctrl_print
#from ...difmiadi_std.printing.controllers import ctrl_print

class wizard_printlabelsale(models.TransientModel):
    _name = "wiz_print_etiq_sale"
    _description = "Wizard print etiquette from sale"
    
    printer_id = fields.Many2one("di.printing.printer", required=True)
    model_id = fields.Many2one("di.printing.etiqmodel", required=True)
    #message = fields.Text(string="Information")
    
#    @api.multi
    def print_etiq(self):
        #FP20190318 avant .file
        #printerName = "\\\\" + self.printer_id.adressIp + "\\" + self.printer_id.realName
        #labelFile = self.model_id.file
        printerName = self.printer_id.name
        labelFile = self.model_id.text 
        informations = [("key1","value1"),("key2","value2"),("key3","value3"),("saleline_qty",1)]
        #ctrl_print.printetiqonwindows(printerName,labelFile,'[',informations)
        self.env['di.printing.printing'].printetiquetteonwindows(printer,labelFile,'[',informations)
        return {'type': 'ir.actions.act_window_close'}  